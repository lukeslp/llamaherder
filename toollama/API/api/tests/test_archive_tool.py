#!/usr/bin/env python
"""
Test script for the archive retrieval tool.
This script tests the functionality of the archive retrieval tool by making requests to the API.
"""

import requests
import json
import sys
import os
import time

# Add the parent directory to sys.path to allow importing API modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Default API URL
API_URL = "http://localhost:8435/v2"

def test_wayback_retrieval():
    """Test retrieving a snapshot from the Wayback Machine."""
    print("\n=== Testing Wayback Machine Retrieval ===")
    
    url = "https://example.com"
    endpoint = f"{API_URL}/tools/archive"
    params = {
        "url": url,
        "provider": "wayback"
    }
    
    try:
        response = requests.get(endpoint, params=params)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Archived URL: {result['archived_url']}")
            print(f"Message: {result['message']}")
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def test_archiveis_retrieval():
    """Test retrieving a snapshot from Archive.is."""
    print("\n=== Testing Archive.is Retrieval ===")
    
    url = "https://example.com"
    endpoint = f"{API_URL}/tools/archive"
    data = {
        "url": url,
        "provider": "archiveis",
        "capture": False  # Just try to find an existing snapshot
    }
    
    try:
        response = requests.post(endpoint, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            if result['success']:
                print(f"Archived URL: {result['archived_url']}")
            print(f"Message: {result['message']}")
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def test_memento_retrieval():
    """Test retrieving a snapshot from Memento Aggregator."""
    print("\n=== Testing Memento Aggregator Retrieval ===")
    
    url = "https://example.com"
    endpoint = f"{API_URL}/tools/archive"
    data = {
        "url": url,
        "provider": "memento"
    }
    
    try:
        response = requests.post(endpoint, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            if result['success']:
                print(f"Archived URL: {result['archived_url']}")
                print(f"Total Snapshots: {result.get('total_snapshots', 'N/A')}")
                print(f"First Snapshot: {result.get('first_snapshot_date', 'N/A')}")
                print(f"Last Snapshot: {result.get('last_snapshot_date', 'N/A')}")
            print(f"Message: {result['message']}")
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def test_direct_tool_execution():
    """Test direct execution of the archive tool."""
    print("\n=== Testing Direct Tool Execution ===")
    
    url = "https://example.com"
    endpoint = f"{API_URL}/tools/execute/get_archived_webpage"
    data = {
        "url": url,
        "provider": "wayback"
    }
    
    try:
        response = requests.post(endpoint, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            if result['success']:
                print(f"Archived URL: {result['archived_url']}")
            print(f"Message: {result['message']}")
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def test_direct_12ft_execution():
    """Test direct execution of the 12ft.io provider."""
    print("\n=== Testing Direct 12ft.io Execution ===")
    
    url = "https://example.com"
    endpoint = f"{API_URL}/tools/execute/get_archived_webpage"
    data = {
        "url": url,
        "provider": "12ft"
    }
    
    try:
        response = requests.post(endpoint, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            if result['success']:
                print(f"12ft.io URL: {result['archived_url']}")
            print(f"Message: {result['message']}")
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def test_schema_endpoint():
    """Test the schema endpoint for the archive tool."""
    print("\n=== Testing Schema Endpoint ===")
    
    endpoint = f"{API_URL}/tools/archive/schema"
    
    try:
        response = requests.get(endpoint)
        
        if response.status_code == 200:
            schema = response.json()
            print(f"Schema retrieved successfully:")
            print(json.dumps(schema, indent=2))
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def test_12ft_retrieval():
    """Test retrieving a webpage through 12ft.io."""
    print("\n=== Testing 12ft.io Retrieval ===")
    
    url = "https://example.com"
    endpoint = f"{API_URL}/tools/archive"
    data = {
        "url": url,
        "provider": "12ft"
    }
    
    try:
        response = requests.post(endpoint, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            if result['success']:
                print(f"12ft.io URL: {result['archived_url']}")
            print(f"Message: {result['message']}")
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and report results."""
    print("=== Running Archive Tool Tests ===")
    
    tests = [
        ("Wayback Machine Retrieval", test_wayback_retrieval),
        ("Archive.is Retrieval", test_archiveis_retrieval),
        ("Memento Aggregator Retrieval", test_memento_retrieval),
        ("12ft.io Retrieval", test_12ft_retrieval),
        ("Direct Tool Execution", test_direct_tool_execution),
        ("Direct 12ft.io Execution", test_direct_12ft_execution),
        ("Schema Endpoint", test_schema_endpoint)
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\nRunning test: {name}")
        start_time = time.time()
        success = test_func()
        end_time = time.time()
        duration = end_time - start_time
        
        results.append({
            "name": name,
            "success": success,
            "duration": duration
        })
    
    # Print summary
    print("\n=== Test Summary ===")
    all_passed = True
    
    for result in results:
        status = "PASSED" if result["success"] else "FAILED"
        all_passed = all_passed and result["success"]
        print(f"{result['name']}: {status} ({result['duration']:.2f}s)")
    
    print(f"\nOverall: {'PASSED' if all_passed else 'FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 