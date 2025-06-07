# Code Snippets from toollama/API/api-tools/tools/Untitled/tree_of_thoughts.py

File: `toollama/API/api-tools/tools/Untitled/tree_of_thoughts.py`  
Language: Python  
Extracted: 2025-06-07 05:20:00  

## Snippet 1
Lines 1-77

```Python
"""
title: mcts
author: av
author_url: https://github.com/av
description: mcts - Monte Carlo Tree Search
version: 0.0.5
"""

import logging
import random
import math
import asyncio
import json
import re

from typing import (
  List,
  Optional,
  AsyncGenerator,
  Callable,
  Awaitable,
  Generator,
  Iterator,
)
from open_webui.constants import TASKS
from open_webui.apps.ollama import main as ollama

# ==============================================================================

name = "mcts"
default_max_children = 2
default_exploration_weight = 1.414
default_max_iterations = 2
default_max_simulations = 2
default_thoughts = 2

# ==============================================================================

thoughts_prompt = """
<instruction>
Give a suggestion on how this answer can be improved.
WRITE ONLY AN IMPROVEMENT SUGGESTION AND NOTHING ELSE.
YOUR REPLY SHOULD BE A SINGLE SENTENCE.
</instruction>

<question>
{question}
</question>

<draft>
{answer}
</draft>
""".strip()

eval_answer_prompt = """
Given the following text:
"{answer}"

How well does it answers this question:
"{question}"

Rate the answer from 1 to 10, where 1 is completely wrong or irrelevant and 10 is a perfect answer.
Reply with a single number between 1 and 10 only. Do not write anything else, it will be discarded.
THINK CAREFULLY AND USE BEST PRACTICES.
""".strip()

analyze_prompt = """
Iteration Analysis:

Original question: {question}
Best answer found: {best_answer}
Best score achieved: {best_score}

Analyze this iteration of the thought process. Consider the following:
1. What aspects of the best answer made it successful?
2. What patterns or approaches led to higher-scoring thoughts?
3. Were there any common pitfalls or irrelevant tangents in lower-scoring thoughts?
```

## Snippet 2
Lines 80-110

```Python
Provide a concise analysis and suggest one specific improvement strategy for the next iteration.
""".strip()

update_prompt = """
<instruction>
Your task is to read the question and the answer below, then analyse the given critique.
When you are done - think about how the answer can be improved based on the critique.
WRITE A REVISED ANSWER THAT ADDRESSES THE CRITIQUE. DO NOT WRITE ANYTHING ELSE.
</instruction>
<question>
{question}
</question>
<draft>
{answer}
</draft>
<critique>
{improvements}
</critique>
""".strip()

initial_prompt = """
<instruction>
Answer the question below. Do not pay attention to, unexpected casing, punctuation or accent marks.
</instruction>

<question>
{question}
</question>
"""

# ==============================================================================
```

## Snippet 3
Lines 115-125

```Python
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.set_name(name)
    formatter = logging.Formatter(
      "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
  return logger
```

## Snippet 4
Lines 128-137

```Python
logger = setup_logger()

# ==============================================================================

mods = [
  "capitalize",
  "diacritic",
  "leetspeak",
  "remove_vowel",
]
```

## Snippet 5
Lines 144-152

```Python
if not 0 <= percentage <= 100:
    raise ValueError("Percentage must be between 0 and 100")

  words = text.split()
  chars = list(text)
  num_chars_to_modify = max(1, int(len(chars) * (percentage / 100)))
  indices_to_modify = random.sample(range(len(chars)), num_chars_to_modify)
  word_mapping = {}
```

## Snippet 6
Lines 153-157

```Python
for idx in indices_to_modify:
    modification = random.choice(mods)

    # Find the word that contains the current character
    current_length = 0
```

## Snippet 7
Lines 174-186

```Python
elif modification == "leetspeak":
      leetspeak_map = {
        "a": "4",
        "e": "3",
        "i": "1",
        "o": "0",
        "s": "5",
        "t": "7",
        "b": "8",
        "g": "9",
        "l": "1",
      }
      chars[idx] = leetspeak_map.get(chars[idx].lower(), chars[idx])
```

## Snippet 8
Lines 191-194

```Python
modified_word = "".join(
      chars[word_start_idx:word_start_idx + len(original_word)]
    )
```

## Snippet 9
Lines 195-200

```Python
if modified_word != original_word:
      # Clean up both the modified word and the original word
      cleaned_modified_word = modified_word.rstrip(".,!?")
      cleaned_original_word = original_word.rstrip(".,!?")
      word_mapping[cleaned_modified_word] = cleaned_original_word
```

## Snippet 10
Lines 206-208

```Python
for key, value in mapping.items():
    text = text.replace(key, value)
  return text
```

## Snippet 11
Lines 218-226

```Python
class Node:
  id: str
  content: str
  parent: Optional["Node"]
  max_children: int
  children: List["Node"]
  visits: int
  value: float
```

## Snippet 12
Lines 227-238

```Python
def __init__(self, **kwargs):
    self.id = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=4))
    self.content = kwargs.get("content")
    self.parent = kwargs.get("parent")
    self.exploration_weight = kwargs.get(
      "exploration_weight", default_exploration_weight
    )
    self.max_children = kwargs.get("max_children", default_max_children)
    self.children = []
    self.visits = 0
    self.value = 0
```

## Snippet 13
Lines 239-243

```Python
def add_child(self, child: "Node"):
    child.parent = self
    self.children.append(child)
    return child
```

## Snippet 14
Lines 247-255

```Python
def uct_value(self):
    epsilon = 1e-6

    return self.value / (self.visits +
                         epsilon) + self.exploration_weight * math.sqrt(
                           math.log(self.parent.visits) /
                           (self.visits + epsilon)
                         )
```

## Snippet 15
Lines 270-273

```Python
if not self.children:
      return self

    return max(self.children, key=lambda child: child.visits).best_child()
```

## Snippet 16
Lines 276-282

```Python
class MCTS:
  question: str
  root: Node
  llm: "Pipe"
  selected: Optional[Node]
  exploration_weight: float
```

## Snippet 17
Lines 283-291

```Python
def __init__(self, **kwargs):
    self.question = kwargs.get("question")
    self.root = kwargs.get("root")
    self.llm = kwargs.get("llm")
    self.selected = None
    self.exploration_weight = kwargs.get(
      "exploration_weight", default_exploration_weight
    )
```

## Snippet 18
Lines 292-294

```Python
async def select(self):
    logger.debug("Selecting node...")
    node = self.root
```

## Snippet 19
Lines 295-298

```Python
while node.children:
      node = self.uct_select(node)
    return node
```

## Snippet 20
Lines 299-302

```Python
async def expand(self, node):
    logger.debug(f"Expanding node {node.id}...")
    await self.llm.progress(f"Thinking about {node.id}...")
```

## Snippet 21
Lines 303-314

```Python
for _ in range(random.randint(default_thoughts, default_thoughts + 1)):
      await self.llm.emit_replace(self.mermaid(node))
      await self.llm.emit_message(f"Thought: ")
      thought = await self.llm.generate_thought(node.content)
      await self.llm.emit_message(f"\n\n---\n\nSolution:\n")

      new_content = await self.llm.update_approach(node.content, thought)
      child = Node(content=new_content, parent=node)
      node.add_child(child)

    return random.choice(node.children)
```

## Snippet 22
Lines 315-321

```Python
async def simulate(self, node):
    logger.debug(f"Simulating node {node.id}...")
    await self.llm.progress(f"Thinking about {node.id}...")
    await self.llm.emit_replace(self.mermaid())

    return await self.llm.evaluate_answer(node.content)
```

## Snippet 23
Lines 324-328

```Python
while node:
      node.visits += 1
      node.value += score
      node = node.parent
```

## Snippet 24
Lines 329-332

```Python
def uct_select(self, node):
    logger.debug(f"Selecting uct {node.id}...")
    return max(node.children, key=lambda child: child.uct_value())
```

## Snippet 25
Lines 363-368

```Python
class Pipe:
  __current_event_emitter__: EventEmitter
  __current_node__: Node
  __question__: str
  __model__: str
```

## Snippet 26
Lines 372-378

```Python
def pipes(self) -> list[dict[str, str]]:
    ollama.get_all_models()
    models = ollama.app.state.MODELS

    out = [
      {
        "id": f"{name}-{key}",
```

## Snippet 27
Lines 381-385

```Python
]
    logger.debug(f"Available models: {out}")

    return out
```

## Snippet 28
Lines 386-390

```Python
def resolve_model(self, body: dict) -> str:
    model_id = body.get("model")
    without_pipe = ".".join(model_id.split(".")[1:])
    return without_pipe.replace(f"{name}-", "")
```

## Snippet 29
Lines 394-404

```Python
async def pipe(
    self,
    body: dict,
    __user__: dict,
    __event_emitter__=None,
    __task__=None,
    __model__=None,
  ) -> str | Generator | Iterator:
    model = self.resolve_model(body)
    base_question = self.resolve_question(body)
```

## Snippet 30
Lines 405-408

```Python
if __task__ == TASKS.TITLE_GENERATION:
      content = await self.get_completion(model, body.get("messages"))
      return f"{name}: {content}"
```

## Snippet 31
Lines 409-429

```Python
logger.debug(f"Pipe {name} received: {body}")
    question, mapping = modify_text(base_question, 0)
    logger.debug(f"Question: {question}")

    # TODO: concurrency
    self.__model__ = model
    self.__question__ = base_question
    self.__current_event_emitter__ = __event_emitter__

    best_answer = None
    best_score = -float("inf")

    await self.progress("Preparing initial thoughts...")
    initial_reply = await self.stream_prompt_completion(
      initial_prompt, question=question
    )

    root = Node(content=initial_reply)
    mcts = MCTS(root=root, llm=self)

    logger.debug("Starting MCTS...")
```

## Snippet 32
Lines 430-438

```Python
for i in range(default_max_iterations):
      logger.debug(f"Iteration {i + 1}/{default_max_iterations}...")

      await mcts.search(default_max_simulations)
      logger.debug(mcts.mermaid())

      best_child = mcts.best_child()
      score = await self.evaluate_answer(best_child.content)
```

## Snippet 33
Lines 439-442

```Python
if score > best_score:
        best_score = score
        best_answer = best_child.content
```

## Snippet 34
Lines 443-449

```Python
await self.emit_replace(mcts.mermaid(best_child))
    await self.emit_message(f"{best_answer}")
    await asyncio.sleep(0.2)
    await self.done()

    return ""
```

## Snippet 35
Lines 450-456

```Python
async def progress(
    self,
    message: str,
  ):
    logger.debug(f"Progress: {message}")
    await self.emit_status("info", message, False)
```

## Snippet 36
Lines 460-469

```Python
async def emit_message(self, message: str):
    await self.__current_event_emitter__(
      {
        "type": "message",
        "data": {
          "content": message
        }
      }
    )
```

## Snippet 37
Lines 470-479

```Python
async def emit_replace(self, message: str):
    await self.__current_event_emitter__(
      {
        "type": "replace",
        "data": {
          "content": message
        }
      }
    )
```

## Snippet 38
Lines 480-485

```Python
async def emit_status(self, level: str, message: str, done: bool):
    await self.__current_event_emitter__(
      {
        "type": "status",
        "data":
          {
```

## Snippet 39
Lines 494-506

```Python
async def get_streaming_completion(
    self,
    model: str,
    messages,
  ) -> AsyncGenerator[str, None]:
    response = await ollama.generate_openai_chat_completion(
      {
        "model": model,
        "messages": messages,
        "stream": True
      }
    )
```

## Snippet 40
Lines 512-519

```Python
async for chunk in self.get_streaming_completion(
      model, [{
        "role": "user",
        "content": content
      }]
    ):
      yield chunk
```

## Snippet 41
Lines 520-530

```Python
async def get_completion(self, model: str, messages):
    response = await ollama.generate_openai_chat_completion(
      {
        "model": model,
        "messages": messages,
        "stream": False
      }
    )

    return self.get_response_content(response)
```

## Snippet 42
Lines 533-540

```Python
async for chunk in self.get_message_completion(
      self.__model__,
      prompt.format(**format_args),
    ):
      complete += chunk
      await self.emit_message(chunk)
    return complete
```

## Snippet 43
Lines 541-545

```Python
async def generate_thought(self, answer):
    return await self.stream_prompt_completion(
      thoughts_prompt, answer=answer, question=self.__question__
    )
```

## Snippet 44
Lines 546-553

```Python
async def analyze_iteration(self, best_answer, best_score):
    return await self.stream_prompt_completion(
      analyze_prompt,
      question=self.__question__,
      best_answer=best_answer,
      best_score=best_score
    )
```

## Snippet 45
Lines 554-561

```Python
async def update_approach(self, answer, improvements):
    return await self.stream_prompt_completion(
      update_prompt,
      question=self.__question__,
      answer=answer,
      improvements=improvements
    )
```

## Snippet 46
Lines 562-574

```Python
async def evaluate_answer(self, answer):
    result = await self.stream_prompt_completion(
      eval_answer_prompt,
      answer=answer,
      question=self.__question__,
    )
    try:
      score = re.search(r"\d+", result).group()
      return int(score)
    except AttributeError:
      logger.error(f"AnswerEval: unable to parse \"{result[:100]}\"")
      return 0
```

## Snippet 47
Lines 575-583

```Python
def get_response_content(self, response):
    try:
      return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
      logger.error(
        f"ResponseError: unable to extract content from \"{response[:100]}\""
      )
      return ""
```

## Snippet 48
Lines 591-595

```Python
if chunk_str == "[DONE]" or not chunk_str:
      return

    try:
      chunk_data = json.loads(chunk_str)
```

