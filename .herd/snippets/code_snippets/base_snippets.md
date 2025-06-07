# Code Snippets from toollama/API/api-tools/tools/tools/tools2/base.py

File: `toollama/API/api-tools/tools/tools/tools2/base.py`  
Language: Python  
Extracted: 2025-06-07 05:25:40  

## Snippet 1
Lines 8-25

```Python
async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True,
        **kwargs
    ) -> AsyncIterator[Dict[str, str]]:
        """Generate chat completions from the AI provider.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters

        Yields:
            Dict containing response chunks with 'type' and 'content' keys
        """
        pass
```

## Snippet 2
Lines 27-46

```Python
async def process_file(
        self,
        file_data: bytes,
        file_type: str,
        task_type: str,
        **kwargs
    ) -> AsyncIterator[Dict[str, str]]:
        """Process a file using the AI provider.

        Args:
            file_data: Raw file bytes
            file_type: MIME type of the file
            task_type: Type of processing (e.g., 'alt_text', 'analysis')
            **kwargs: Additional provider-specific parameters

        Yields:
            Dict containing response chunks with 'type' and 'content' keys
        """
        pass
```

## Snippet 3
Lines 48-52

```Python
async def embeddings(
        self,
        text: Union[str, List[str]],
        **kwargs
    ) -> List[List[float]]:
```

## Snippet 4
Lines 53-62

```Python
"""Generate embeddings for text using the AI provider.

        Args:
            text: Single string or list of strings to embed
            **kwargs: Additional provider-specific parameters

        Returns:
            List of embedding vectors
        """
        pass
```

