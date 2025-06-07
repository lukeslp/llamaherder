"""
Blueprint for Dreamwalker routes.
"""

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import asyncio
import logging
import uuid
import time
from typing import Dict, Any, List, Optional

# Import the Dreamwalker classes
from api.dreamwalker import BaseDreamwalker, SwarmDreamwalker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create blueprint
dreamwalker_bp = Blueprint('dreamwalker', __name__)

# In-memory storage for active workflows
active_workflows: Dict[str, BaseDreamwalker] = {}

# Helper function to run async code in sync context
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Helper function to execute workflow in background
def execute_workflow_background(workflow_id: str, query: str, workflow_type: str, model: Optional[str] = None):
    """
    Execute a workflow in the background.
    
    Args:
        workflow_id: Unique identifier for the workflow
        query: The query to process
        workflow_type: Type of workflow to execute
        model: Model to use for the workflow
    """
    try:
        # Get the workflow instance
        workflow = active_workflows.get(workflow_id)
        if not workflow:
            logger.error(f"Workflow {workflow_id} not found for background execution")
            return
        
        logger.info(f"Starting background execution of workflow {workflow_id} with query: {query}")
        # Execute the workflow
        run_async(workflow.execute(query, model=model))
        logger.info(f"Background execution completed for workflow {workflow_id}")
    except Exception as e:
        logger.error(f"Error executing workflow {workflow_id}: {str(e)}", exc_info=True)
        # If an error occurs, update the workflow status
        if workflow_id in active_workflows:
            active_workflows[workflow_id].fail(str(e))

# Decorator to handle CORS for all routes in this blueprint
def cors_enabled(f):
    """Custom decorator to add CORS headers to responses"""
    def decorated(*args, **kwargs):
        # Log preflight requests
        if request.method == 'OPTIONS':
            logger.debug(f"Handling OPTIONS preflight request for {request.path}")
            
        # Log all request details for debugging
        logger.debug(f"Request method: {request.method}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        logger.debug(f"Request origin: {request.headers.get('Origin', 'No origin header')}")
        logger.debug(f"Request path: {request.path}")
        
        # Call the original function
        response = f(*args, **kwargs)
        
        # Add CORS headers to the response
        origin = request.headers.get('Origin', '*')
        
        # Log response details
        logger.debug(f"Response before CORS headers: {response}")
        logger.debug(f"Setting Access-Control-Allow-Origin: {origin}")
        
        # If it's a flask.Response object, add headers directly
        if hasattr(response, 'headers'):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key, Accept, Origin, User-Agent'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
            response.headers['Vary'] = 'Origin'
            
            # Log the response headers
            logger.debug(f"Response headers after CORS: {dict(response.headers)}")
        else:
            # If it's not a Response object, it could be a tuple containing a dict and status code
            logger.warning(f"Response is not a direct Response object: {type(response)}")
            
        return response
    
    # Preserve the function name and docstring
    decorated.__name__ = f.__name__
    decorated.__doc__ = f.__doc__
    return decorated

@dreamwalker_bp.route('/search', methods=['POST', 'OPTIONS'])
@cors_enabled
def start_search_workflow():
    """
    Start a new search workflow.
    
    This endpoint initiates a new search workflow based on the provided query.
    The workflow runs asynchronously in the background, and the response includes
    a workflow_id that can be used to check the status and retrieve results.
    """
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        logger.info("Handling OPTIONS preflight request for /search")
        response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
        return response
        
    try:
        # Log request details
        logger.info(f"Received search request: {request.method}")
        logger.info(f"Request Content-Type: {request.headers.get('Content-Type')}")
        
        # Parse request data
        if request.is_json:
            data = request.get_json()
            logger.info(f"Parsed JSON data: {data}")
        else:
            # Try to parse form data
            try:
                data = request.form.to_dict()
                logger.info(f"Parsed form data: {data}")
            except Exception as form_error:
                logger.error(f"Error parsing form data: {str(form_error)}")
                data = None
        
        if not data:
            error_msg = "No data provided or unsupported Content-Type"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 400
        
        query = data.get('query')
        if not query:
            error_msg = "No query provided"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 400
        
        workflow_type = data.get('workflow_type', 'swarm')
        model = data.get('model')
        
        logger.info(f"Processing search request: query='{query}', workflow_type='{workflow_type}', model='{model}'")
        
        # Generate a unique workflow ID
        workflow_id = str(uuid.uuid4())
        logger.info(f"Generated new workflow ID: {workflow_id}")
        
        # Create the appropriate workflow instance
        if workflow_type.lower() == "swarm":
            logger.info(f"Creating SwarmDreamwalker instance with model: {model}")
            workflow = SwarmDreamwalker(workflow_id=workflow_id, model=model)
        else:
            error_msg = f"Unsupported workflow type: {workflow_type}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 400
        
        # Store the workflow in memory
        active_workflows[workflow_id] = workflow
        logger.info(f"Stored workflow {workflow_id} in active_workflows")
        
        # Start the workflow in a background thread
        import threading
        thread = threading.Thread(
            target=execute_workflow_background,
            args=(workflow_id, query, workflow_type, model)
        )
        thread.daemon = True
        thread.start()
        logger.info(f"Started background thread for workflow {workflow_id}")
        
        # Return the initial response
        response_data = {
            "workflow_id": workflow_id,
            "status": workflow.status,
            "progress": workflow.progress,
            "step_description": workflow.step_description
        }
        logger.info(f"Returning initial response: {response_data}")
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error starting workflow: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@dreamwalker_bp.route('/status/<workflow_id>', methods=['GET', 'OPTIONS'])
@cors_enabled
def get_workflow_status(workflow_id):
    """
    Get the status of a workflow.
    
    This endpoint returns the current status of a workflow, including progress,
    step description, and results if the workflow has completed.
    """
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        logger.info(f"Handling OPTIONS preflight request for /status/{workflow_id}")
        response = jsonify({"allowed_methods": ["GET", "OPTIONS"]})
        return response
        
    try:
        logger.info(f"Getting status for workflow: {workflow_id}")
        
        # Check if the workflow exists
        if workflow_id not in active_workflows:
            error_msg = f"Workflow not found: {workflow_id}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 404
        
        # Get the workflow
        workflow = active_workflows[workflow_id]
        
        # Return the workflow status
        status_data = workflow.to_dict()
        logger.info(f"Returning status for workflow {workflow_id}: {status_data}")
        return jsonify(status_data)
    
    except Exception as e:
        logger.error(f"Error getting workflow status: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@dreamwalker_bp.route('/result/<workflow_id>', methods=['GET', 'OPTIONS'])
@cors_enabled
def get_workflow_result(workflow_id):
    """
    Get the result of a completed workflow.
    
    This endpoint returns the result of a completed workflow. If the workflow
    is still running or has failed, an appropriate error is returned.
    """
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        logger.info(f"Handling OPTIONS preflight request for /result/{workflow_id}")
        response = jsonify({"allowed_methods": ["GET", "OPTIONS"]})
        return response
        
    try:
        logger.info(f"Getting result for workflow: {workflow_id}")
        
        # Check if the workflow exists
        if workflow_id not in active_workflows:
            error_msg = f"Workflow not found: {workflow_id}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 404
        
        # Get the workflow
        workflow = active_workflows[workflow_id]
        
        # Check if the workflow has completed
        if workflow.status != "completed":
            if workflow.status == "failed":
                error_msg = f"Workflow failed: {workflow.error}"
                logger.error(error_msg)
                return jsonify({"error": error_msg}), 400
            else:
                error_msg = f"Workflow is still running (status: {workflow.status})"
                logger.warning(error_msg)
                return jsonify({"error": error_msg}), 400
        
        # Return the workflow result
        logger.info(f"Returning result for workflow {workflow_id}")
        return jsonify(workflow.results)
    
    except Exception as e:
        logger.error(f"Error getting workflow result: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@dreamwalker_bp.route('/cancel/<workflow_id>', methods=['DELETE', 'OPTIONS'])
@cors_enabled
def cancel_workflow(workflow_id):
    """
    Cancel a running workflow.
    
    This endpoint cancels a running workflow and returns its final status.
    """
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        logger.info(f"Handling OPTIONS preflight request for /cancel/{workflow_id}")
        response = jsonify({"allowed_methods": ["DELETE", "OPTIONS"]})
        return response
        
    try:
        logger.info(f"Cancelling workflow: {workflow_id}")
        
        # Check if the workflow exists
        if workflow_id not in active_workflows:
            error_msg = f"Workflow not found: {workflow_id}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 404
        
        # Get the workflow
        workflow = active_workflows[workflow_id]
        
        # Cancel the workflow if it's still running
        if workflow.status == "running":
            logger.info(f"Cancelling running workflow: {workflow_id}")
            workflow.cancel("Cancelled by user")
        else:
            logger.info(f"Workflow {workflow_id} is not running (status: {workflow.status}), no need to cancel")
        
        # Return the workflow status
        status_data = workflow.to_dict()
        logger.info(f"Returning status after cancellation: {status_data}")
        return jsonify(status_data)
    
    except Exception as e:
        logger.error(f"Error cancelling workflow: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@dreamwalker_bp.route('/list', methods=['GET', 'OPTIONS'])
@cors_enabled
def list_workflows():
    """
    List active workflows.
    
    This endpoint returns a list of active workflows, optionally filtered by status.
    """
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        logger.info("Handling OPTIONS preflight request for /list")
        response = jsonify({"allowed_methods": ["GET", "OPTIONS"]})
        return response
        
    try:
        logger.info("Listing workflows")
        
        # Get query parameters
        status = request.args.get('status')
        limit = int(request.args.get('limit', 10))
        
        logger.info(f"List parameters: status={status}, limit={limit}")
        
        # Filter workflows by status if provided
        if status:
            filtered_workflows = [w for w in active_workflows.values() if w.status == status]
            logger.info(f"Filtered {len(filtered_workflows)} workflows with status '{status}'")
        else:
            filtered_workflows = list(active_workflows.values())
            logger.info(f"Retrieved all {len(filtered_workflows)} workflows")
        
        # Sort workflows by start time (newest first)
        sorted_workflows = sorted(filtered_workflows, key=lambda w: w.start_time or 0, reverse=True)
        
        # Limit the number of workflows returned
        limited_workflows = sorted_workflows[:limit]
        logger.info(f"Limited to {len(limited_workflows)} workflows")
        
        # Return the workflow statuses
        result = [w.to_dict() for w in limited_workflows]
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@dreamwalker_bp.route('/cleanup', methods=['DELETE', 'OPTIONS'])
@cors_enabled
def cleanup_workflows():
    """
    Clean up old workflows.
    
    This endpoint removes old workflows from memory based on their status and age.
    """
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        logger.info("Handling OPTIONS preflight request for /cleanup")
        response = jsonify({"allowed_methods": ["DELETE", "OPTIONS"]})
        return response
        
    try:
        logger.info("Cleaning up workflows")
        
        # Get query parameters
        status = request.args.get('status', 'completed')
        age_hours = int(request.args.get('age_hours', 24))
        
        logger.info(f"Cleanup parameters: status={status}, age_hours={age_hours}")
        
        # Calculate the cutoff time
        cutoff_time = time.time() - (age_hours * 3600)
        
        # Find workflows to remove
        workflows_to_remove = []
        for workflow_id, workflow in active_workflows.items():
            if workflow.status == status and workflow.end_time and workflow.end_time < cutoff_time:
                workflows_to_remove.append(workflow_id)
        
        logger.info(f"Found {len(workflows_to_remove)} workflows to remove")
        
        # Remove the workflows
        for workflow_id in workflows_to_remove:
            logger.info(f"Removing workflow: {workflow_id}")
            del active_workflows[workflow_id]
        
        # Return the result
        result = {
            "status": "success",
            "removed_count": len(workflows_to_remove),
            "remaining_count": len(active_workflows)
        }
        
        logger.info(f"Cleanup completed: {result}")
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error cleaning up workflows: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500 