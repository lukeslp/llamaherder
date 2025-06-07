function processMessage(content) {
  try {
    if (!content) {
      const messageContainer = document.createElement('div');
      messageContainer.className = 'markdown-body message-content';
      messageContainer.textContent = 'Thinking...';
      return messageContainer;
    }

    const messageContainer = document.createElement('div');
    messageContainer.className = 'markdown-body message-content';
    
    try {
      // Use DOMPurify to safely sanitize content before sending to marked
      const sanitizedContent = DOMPurify.sanitize(content);
      
      messageContainer.innerHTML = marked.parse(sanitizedContent, {
        breaks: true,
        gfm: true,
        headerIds: true,
        mangle: false
      });

      // Highlight code blocks if any
      messageContainer.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
        
        // Add copy button to code blocks
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.textContent = 'Copy';
        copyButton.addEventListener('click', () => {
          const code = block.textContent;
          navigator.clipboard.writeText(code).then(() => {
            copyButton.textContent = 'Copied!';
            setTimeout(() => {
              copyButton.textContent = 'Copy';
            }, 2000);
          }).catch(err => {
            console.error('Failed to copy: ', err);
            copyButton.textContent = 'Failed';
          });
        });
        
        block.parentElement.insertBefore(copyButton, block);
      });
    } catch (parseError) {
      console.warn('Markdown parsing error:', parseError);
      // Fall back to plaintext display if parsing fails
      messageContainer.textContent = content;
    }
    
    return messageContainer;
  } catch (error) {
    console.error('Error processing message:', error);
    const errorContainer = document.createElement('div');
    errorContainer.className = 'markdown-body message-content error';
    errorContainer.textContent = `Error processing message: ${error.message}`;
    return errorContainer;
  }
}

function sanitizeMessageContent(content) {
  if (!content) return '';
  
  // Only escape < and > in plaintext contexts, not for markdown code blocks
  return content.trim();
}

function createMessageItem(message) {
  try {
    const { content, type } = message;
    const messagesList = document.querySelector('.message-container');
    
    const container = document.createElement('div');
    container.className = `message-wrapper ${type}-wrapper`;
    
    const messageItem = document.createElement('div');
    messageItem.className = `message ${type}`;
    
    const processedContent = processMessage(content);
    messageItem.appendChild(processedContent);
    
    if (type === 'bot-message') {
      const metadataEl = document.createElement('div');
      metadataEl.className = 'message-metadata';
      
      const tokenCountEl = document.createElement('span');
      tokenCountEl.className = 'token-count';
      tokenCountEl.textContent = 'Calculating tokens...';
      
      metadataEl.appendChild(tokenCountEl);
      container.appendChild(messageItem);
      container.appendChild(metadataEl);
      messagesList.appendChild(container);
      
      return { messageItem, tokenCountEl, container };
    } else {
      container.appendChild(messageItem);
      messagesList.appendChild(container);
      return { messageItem };
    }
  } catch (error) {
    console.error('Error creating message item:', error);
    const errorItem = document.createElement('div');
    errorItem.className = 'message error';
    errorItem.textContent = `Error creating message: ${error.message}`;
    return { messageItem: errorItem };
  }
}

function autoScroll() {
  const chatBox = document.querySelector('.message-container');
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to update file name display when a file is selected
function updateFileName() {
  const fileUpload = document.getElementById('fileUpload');
  const fileName = document.getElementById('fileName');
  
  if (fileUpload && fileName) {
    fileUpload.addEventListener('change', function() {
      if (fileUpload.files.length > 0) {
        const file = fileUpload.files[0];
        fileName.textContent = file.name;
        console.log(`File selected: ${file.name} (${file.size} bytes)`);
      } else {
        fileName.textContent = '';
      }
    });
  }
}

// Initialize file upload on page load
document.addEventListener('DOMContentLoaded', function() {
  updateFileName();
  
  // Initialize debug mode checkbox
  const debugModeEl = document.getElementById('debugMode');
  if (debugModeEl) {
    // Default to checked for easier testing
    debugModeEl.checked = true;
  }
});

async function sendChatMessage(message) {
  try {
    console.log('Sending message to API:', message);
    
    // Get option values with null checks
    const webSearchEl = document.getElementById('webSearch');
    const fileSearchEl = document.getElementById('fileSearch');
    const computerUseEl = document.getElementById('computerUse');
    const useFunctionCallingEl = document.getElementById('useFunctionCalling');
    
    const webSearch = webSearchEl ? webSearchEl.checked : false;
    const fileSearch = fileSearchEl ? fileSearchEl.checked : false;
    const computerUse = computerUseEl ? computerUseEl.checked : false;
    const useFunctionCalling = useFunctionCallingEl ? useFunctionCallingEl.checked : false;
    
    const fileUpload = document.getElementById('fileUpload') ? document.getElementById('fileUpload').files[0] : null;
    
    // Create form data for the responses endpoint
    const formData = new FormData();
    
    // Use the hardcoded API key from config
    const hardcodedApiKey = "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";
    
    // Send key 'prompt' (the server expects this) and omit extra keys like max_tokens
    formData.append('prompt', message);
    formData.append('model', 'gpt-4o-2024-11-20');
    formData.append('api_key', hardcodedApiKey);
    
    // Add the advanced capabilities if selected
    if (webSearch) {
      formData.append('web_search', 'true');
    }
    
    if (fileSearch) {
      formData.append('file_search', 'true');
    }
    
    if (computerUse) {
      formData.append('computer_use', 'true');
    }
    
    // Force debug_mode to false so the real API call is made
    formData.append('debug_mode', 'false');
    
    // Example weather tool for demonstration
    const weatherTool = {
      type: "function",
      function: {
        name: "get_weather",
        parameters: {
          location: "Seattle, WA"
        }
      }
    };
    
    // Add tools if function calling is enabled
    if (useFunctionCalling) {
      formData.append('tools', JSON.stringify([weatherTool]));
    }
    
    // If a file is uploaded, use it; otherwise, create a text file from the message
    if (fileUpload) {
      console.log('Uploading file:', fileUpload.name, fileUpload.type, fileUpload.size + ' bytes');
      formData.append('file', fileUpload);
    } else {
      // Create a text file from the message
      console.log('Creating text file from message');
      const messageBlob = new Blob([message], { type: 'text/plain' });
      formData.append('file', messageBlob, 'message.txt');
    }
    
    // Log form data contents for debugging
    for (const pair of formData.entries()) {
      console.log(`${pair[0]}: ${pair[1] instanceof File ? `File: ${pair[1].name} (${pair[1].size} bytes)` : pair[1]}`);
    }
    
    // Always use the production endpoint with HTTPS
    const apiEndpoint = "https://api.assisted.space/v2/responses";
    console.log(`Sending request to ${apiEndpoint}`);
    
    console.log('USING REAL API - NO MOCK RESPONSES');
    console.log(`API Key: ${hardcodedApiKey.substring(0, 10)}...${hardcodedApiKey.substring(hardcodedApiKey.length - 5)}`);
    
    // Make the API request with robust error handling
    try {
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'X-API-Key': hardcodedApiKey
        },
        body: formData
      });

      console.log('REAL API Response status:', response.status);
      console.log('REAL API Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        let errorText = 'Unknown error';
        try {
          const errorData = await response.text();
          errorText = errorData;
          console.error('REAL API Error response:', errorData);
          
          // Try to parse as JSON if possible
          try {
            const errorJson = JSON.parse(errorData);
            if (errorJson.error) {
              errorText = errorJson.error;
            }
          } catch (jsonError) {
            // Not JSON, use text as is
          }
        } catch (textError) {
          console.error('Failed to extract error text:', textError);
        }
        
        throw new Error(`REAL API Error: ${response.statusText} - ${errorText}`);
      }

      return response;
    } catch (fetchError) {
      // Specific error handling for network issues
      console.error(`Fetch error: ${fetchError.message}`);
      
      if (fetchError.message.includes('SSL')) {
        console.error('SSL error detected.');
      }
      
      if (fetchError.message.includes('Failed to fetch')) {
        console.error('Network error - possible CORS or connection issue.');
        console.error('Recommend checking server CORS configuration and network connection.');
      }
      
      throw fetchError;
    }
  } catch (error) {
    console.error('Chat API Error:', error);
    throw error;
  }
}

async function handleMessage(content) {
  try {
    // Get file upload with null check
    const fileUploadEl = document.getElementById('fileUpload');
    const fileUpload = fileUploadEl && fileUploadEl.files.length > 0 ? fileUploadEl.files[0] : null;
    
    // Set a default prompt if there's a file but no message
    if (!content.trim() && fileUpload) {
      content = "Please analyze this file.";
    }
    
    // Validate that either content or file is provided
    if (!content.trim()) {
      alert('Please enter a message');
      return;
    }
    
    // Create and display user message
    const { messageItem: userMessageItem } = createMessageItem({
      content: fileUpload ? `${content} [File: ${fileUpload.name}]` : content,
      type: 'user-message'
    });

    // Create placeholder for bot response
    const { messageItem: botMessageItem, tokenCountEl } = createMessageItem({
      content: 'Sending request to OpenAI Responses API...',
      type: 'bot-message'
    });

    try {
      // Set status to indicate processing
      tokenCountEl.textContent = 'Status: Sending request...';
      
      // Get response from API
      const response = await sendChatMessage(content);
      
      // Update status
      tokenCountEl.textContent = 'Status: Processing response...';
      
      // Parse the response as JSON
      const responseData = await response.json();
      console.log('API response data:', responseData);
      
      // Check if response contains a response_id (which it should for OpenAI Responses)
      if (responseData.response_id) {
        // Update status with current status from API
        tokenCountEl.textContent = `Status: ${responseData.status || 'Processing'} (ID: ${responseData.response_id})`;
        console.log(`Response has ID: ${responseData.response_id}, Status: ${responseData.status}`);
        
        // If the response is already completed, show content immediately
        if (responseData.status === 'completed' && responseData.content) {
          console.log('Content available immediately');
          botMessageItem.innerHTML = '';
          botMessageItem.appendChild(processMessage(responseData.content));
          autoScroll();
          
          // Update token count if available
          if (responseData.usage) {
            const totalTokens = responseData.usage.total_tokens;
            tokenCountEl.textContent = `Tokens: ${totalTokens}`;
          } else {
            tokenCountEl.textContent = 'Response complete';
          }
        } else {
          // Start polling for the complete response - needed for document processing
          console.log('Response not yet complete, starting polling');
          await pollForResponse(responseData.response_id, botMessageItem, tokenCountEl);
        }
      } else if (responseData.content) {
        // Update with content if it's immediately available (unlikely with OpenAI Responses)
        console.log('Content available immediately without response_id');
        botMessageItem.innerHTML = '';
        botMessageItem.appendChild(processMessage(responseData.content));
        autoScroll();
        
        // Update token count if available
        if (responseData.usage) {
          const totalTokens = responseData.usage.total_tokens;
          tokenCountEl.textContent = `Tokens: ${totalTokens}`;
        } else {
          tokenCountEl.textContent = 'Response complete';
        }
      } else if (responseData.error) {
        // Handle error in the response
        console.error('Error in API response:', responseData.error);
        botMessageItem.className = 'message error-message';
        botMessageItem.textContent = `Error: ${responseData.error}`;
        tokenCountEl.textContent = 'Error occurred';
      } else {
        // Handle unexpected response format
        console.warn('Unexpected response format:', responseData);
        botMessageItem.innerHTML = '';
        botMessageItem.appendChild(processMessage(
          'Received an unexpected response format from the API. See details below:\n\n```json\n' + 
          JSON.stringify(responseData, null, 2) + 
          '\n```'
        ));
        tokenCountEl.textContent = 'Unexpected response format';
      }
    } catch (error) {
      console.error('Response processing error:', error);
      botMessageItem.className = 'message error-message';
      botMessageItem.textContent = `Error processing response: ${error.message}`;
      tokenCountEl.textContent = 'Error occurred';
    }

  } catch (error) {
    console.error('Message handling error:', error);
    createMessageItem({
      content: `Error: ${error.message}`,
      type: 'error-message'
    });
  }
}

// Updated polling function with better error handling and more informative status updates
async function pollForResponse(responseId, messageItem, statusElement, maxAttempts = 30, delay = 2000) {
  let attempts = 0;
  console.log(`Starting polling for response ID: ${responseId}`);
  
  // Use the hardcoded API key from config
  const hardcodedApiKey = "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";
  
  // Always use the production endpoint with HTTPS
  const apiEndpoint = "https://api.assisted.space";

  while (attempts < maxAttempts) {
    attempts++;
    statusElement.textContent = `Status: Checking for results (attempt ${attempts}/${maxAttempts})`;
    console.log(`Polling attempt ${attempts}/${maxAttempts}`);
    
    try {
      // Get the response status - include API key in both query parameter and header
      const pollUrl = `${apiEndpoint}/v2/responses/${responseId}?api_key=${encodeURIComponent(hardcodedApiKey)}`;
      console.log(`Polling URL: ${pollUrl}`);
      
      const response = await fetch(pollUrl, {
        headers: {
          'X-API-Key': hardcodedApiKey
        }
      });
      console.log(`Poll response status: ${response.status}`);
      
      if (!response.ok) {
        throw new Error(`Failed to get response status: ${response.status}`);
      }
      
      const responseData = await response.json();
      console.log('Poll parsed response:', responseData);
      
      if (responseData.status === 'completed' && responseData.content) {
        // We have the complete response
        console.log('Polling complete - response received');
        messageItem.innerHTML = '';
        messageItem.appendChild(processMessage(responseData.content));
        autoScroll();
        
        // Update token count if available
        if (responseData.usage) {
          const totalTokens = responseData.usage.total_tokens;
          statusElement.textContent = `Tokens: ${totalTokens}`;
        } else {
          statusElement.textContent = 'Response complete';
        }
        
        return;
      } else if (responseData.status === 'error') {
        // Handle error
        console.error('Error status received during polling:', responseData);
        messageItem.className = 'message error-message';
        messageItem.textContent = `Error: ${responseData.message || responseData.error || 'Unknown error'}`;
        statusElement.textContent = 'Error occurred';
        return;
      } else {
        // Still processing, update status and progress
        console.log(`Still processing: ${responseData.status}`);
        
        let statusText = `Status: ${responseData.status || 'Processing'}`;
        
        // If we have progress information, show that
        if (responseData.progress !== undefined) {
          statusText += ` (${responseData.progress}%)`;
        }
        
        statusElement.textContent = statusText;
        
        // Create meaningful progress display
        const progressContent = document.createElement('div');
        progressContent.className = 'progress-content';
        
        // Add title
        const titleEl = document.createElement('h4');
        titleEl.textContent = 'Processing Request...';
        titleEl.className = 'progress-title';
        progressContent.appendChild(titleEl);
        
        // Add status
        const statusEl = document.createElement('div');
        statusEl.textContent = `Status: ${responseData.status || 'Processing'}`;
        statusEl.className = 'progress-status';
        progressContent.appendChild(statusEl);
        
        // Add progress
        if (responseData.progress !== undefined) {
          const progressBarContainer = document.createElement('div');
          progressBarContainer.className = 'progress-bar-container';
          
          const progressBar = document.createElement('div');
          progressBar.className = 'progress-bar';
          progressBar.style.width = `${responseData.progress}%`;
          
          progressBarContainer.appendChild(progressBar);
          progressContent.appendChild(progressBarContainer);
        }
        
        // Add step description if available
        if (responseData.step_description) {
          const stepEl = document.createElement('div');
          stepEl.className = 'step-description';
          stepEl.textContent = responseData.step_description;
          progressContent.appendChild(stepEl);
        }
        
        // Update the message content
        messageItem.innerHTML = '';
        messageItem.appendChild(progressContent);
      }
    } catch (error) {
      console.error('Error polling for response:', error);
      statusElement.textContent = `Error: ${error.message}`;
    }
    
    // Wait before trying again
    await new Promise(resolve => setTimeout(resolve, delay));
  }
  
  // If we've reached max attempts, show a timeout message
  console.error(`Polling timed out after ${maxAttempts} attempts`);
  messageItem.className = 'message error-message';
  messageItem.textContent = 'Response timed out. The server is still processing your request, but we have stopped waiting for the response.';
  statusElement.textContent = 'Timed out';
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
  const sendButton = document.getElementById('sendButton');
  const messageInput = document.getElementById('messageInput');
  const fileUpload = document.getElementById('fileUpload');
  const fileName = document.getElementById('fileName');

  // Only add event listeners if elements exist
  if (fileUpload && fileName) {
    // Display selected file name
    fileUpload.addEventListener('change', () => {
      if (fileUpload.files.length > 0) {
        fileName.textContent = fileUpload.files[0].name;
      } else {
        fileName.textContent = '';
      }
    });
  }

  if (sendButton && messageInput) {
    sendButton.addEventListener('click', () => {
      console.log('Send button clicked via event listener');
      const content = messageInput.value.trim();
      if (content) {
        handleMessage(content);
        messageInput.value = '';
        // Clear file upload after sending
        if (fileUpload) {
          fileUpload.value = '';
          if (fileName) {
            fileName.textContent = '';
          }
        }
      }
    });

    messageInput.addEventListener('keypress', (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendButton.click();
      }
    });
  }
}); 