# Code Snippets from toollama/soon/tools_pending/unprocessed/dev_epaperless.py

File: `toollama/soon/tools_pending/unprocessed/dev_epaperless.py`  
Language: Python  
Extracted: 2025-06-07 05:15:50  

## Snippet 1
Lines 1-20

```Python
"""
title: Tool to interact with paperless documents
author: Jonas Leine
funding_url: https://github.com/JLeine/open-webui
version: 1.1.0
license: MIT
"""
import json
import os
import requests
import unittest
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from pydantic import BaseModel, Field
from typing import Callable, Any
from typing import Iterator, Optional

load_dotenv()
```

## Snippet 2
Lines 25-27

```Python
if isinstance(obj, Document):
            return {"page_content": obj.page_content, "metadata": obj.metadata}
        return super().default(obj)
```

## Snippet 3
Lines 33-42

```Python
def __init__(self, documentTypeName: Optional[str] = '', documentTagName: Optional[str] = '',
                 correspondent: Optional[str] = '', url: Optional[str] = '',
                 token: Optional[str] = '', created_year: Optional[int] = None,
                 created_month: Optional[int] = None) -> None:
        """Initialize the loader with a document_type.

        Args:
            documentTypeName: The name of the document type to load.
            documentTagName: The name of the document TAG to load.
            url: The URL to load documents from (optional).
```

## Snippet 4
Lines 43-45

```Python
token: The authorization token for API access (optional).
            created_year: The year the documents were created (optional).
            created_month: The month the documents were created (optional).
```

## Snippet 5
Lines 62-71

```Python
def lazy_load(self) -> Iterator[Document]:  # <-- Does not take any arguments
        """A lazy loader that requests all documents from paperless.
        """
        querystring = {"document_type__name__icontains": self.documentTypeName,
                       "tags__name__icontains": self.documentTagName, "created__month": self.created_month,
                       "created_year": self.created_year, "correspondent__name__icontains": self.correspondent}

        headers = {"Authorization": f"Token {self.token}"}
        response = requests.get(self.url, headers=headers, params=querystring)
```

## Snippet 6
Lines 75-81

```Python
for result in data['results']:
                # Include all keys and values in the metadata
                metadata = {"source": f"{self.url.replace('/api', '')}{result['id']}", **result
                            # Merge the result dictionary into metadata
                            }

                # Remove any keys with None values or list values from metadata
```

## Snippet 7
Lines 82-84

```Python
metadata = {k: v for k, v in metadata.items() if v is not None and not isinstance(v, list)}

                yield Document(page_content=result["content"], metadata=metadata, )
```

## Snippet 8
Lines 101-103

```Python
if self.event_emitter:
            await self.event_emitter(
                {"type": "status", "data": {"status": status, "description": description, "done": done, }, })
```

## Snippet 9
Lines 107-111

```Python
class Valves(BaseModel):
        PAPERLESS_URL: str = Field(default="https://paperless.yourdomain.com/",
                                   description="The domain of your paperless service", )
        PAPERLESS_TOKEN: str = Field(default="", description="The token to read docs from paperless", )
```

## Snippet 10
Lines 115-121

```Python
async def get_paperless_documents(self, documentTypeName: Optional[str] = None,
                                      documentTagName: Optional[str] = None,
                                      correspondent: Optional[str] = None,
                                      created_year: Optional[int] = None,
                                      created_month: Optional[int] = None,
                                      __event_emitter__: Callable[[dict], Any] = None) -> str:
        """
```

## Snippet 11
Lines 122-126

```Python
Search for paperless documents and retrieve the content of relevant documents.

        :param documentTypeName: The documentTypeName the user is looking for. If the user does not specifiy anything skip it.
        :param documentTagName: The documentTagName the user is looking for. If the user does not specifiy anything skip it.
        :param correspondent: The correspondent the user is looking for. If the user does not specifiy anything skip it.
```

## Snippet 12
Lines 127-133

```Python
:param created_month: the month where the the documents were created as int. If he asks for June this value is then 6. If the user does not specifiy anything skip it.
        :param created_year: the year where the the documents were created as int. If the user does not specify anything skip it.
        :return: All documents as a JSON string or an error as a string
        """
        emitter = EventEmitter(__event_emitter__)

        try:
```

## Snippet 13
Lines 134-142

```Python
await emitter.progress_update(f"Getting documents for {documentTypeName}")

            error_message = f"Error: Invalid documentTypeName: {documentTypeName}"
            loader = PaperlessDocumentLoader(documentTypeName=documentTypeName, documentTagName=documentTagName,
                                             url=self.valves.PAPERLESS_URL,
                                             token=self.valves.PAPERLESS_TOKEN, created_month=created_month,
                                             created_year=created_year, correspondent=correspondent)
            documents = loader.load()
```

## Snippet 14
Lines 144-147

```Python
error_message = f"Query returned 0 for correspondent {correspondent} documentTypeName {documentTypeName} documentTag {documentTagName} month {created_month} year {created_year}"
                await emitter.error_update(error_message)
                return error_message
```

## Snippet 15
Lines 152-157

```Python
for document in decoded_documents:
                    await __event_emitter__({"type": "citation", "data": {"document": [document["page_content"]],
                                                                          "metadata": [{"source": document["metadata"][
                                                                              "title"]}], "source": {
                            "name": document["metadata"]["source"]}, }, })
```

## Snippet 16
Lines 161-164

```Python
except Exception as e:
            error_message = f"Error: {str(e)}"
            await emitter.error_update(error_message)
            return error_message
```

## Snippet 17
Lines 168-175

```Python
async def assert_document_response(self, documentTypeName: str, expected_documents: int):
        paperless_tool = Tools()
        paperless_tool.valves.PAPERLESS_URL = os.getenv("PAPERLESS_URL")
        paperless_tool.valves.PAPERLESS_TOKEN = os.getenv("PAPERLESS_API_KEY")
        documents = await paperless_tool.get_paperless_documents(documentTypeName, "YourTagType", "YourCorrespondent", 2024, 7)
        decoded_documents = json.loads(documents)
        self.assertEqual(len(decoded_documents), expected_documents)
```

## Snippet 18
Lines 176-179

```Python
async def assert_paperless_error(self, documentTypeName: str):
        response = await Tools().get_paperless_documents(documentTypeName)
        self.assertTrue("Query returned 0" in response)
```

## Snippet 19
Lines 180-183

```Python
async def test_get_documents(self):
        documentType = "YourDocumentType"
        await self.assert_document_response(documentType, 11)
```

## Snippet 20
Lines 184-186

```Python
async def test_get_paperless_documents_with_invalid_documentTypeName(self):
        invalid_documentTypeName = "DoesNotExist"
        await self.assert_paperless_error(invalid_documentTypeName)
```

