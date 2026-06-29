import json
import os

MEMORY_FILE = "memory.json"
MAX_MEMORY_MESSAGES = 12


def prune_memory(messages):
    """Keep only recent user and assistant messages in memory."""
    filtered = []
    for message in messages:
        if message["role"] == "user":
            filtered.append({"role": "user", "content": message.get("content", "")})
        elif message["role"] == "assistant" and message.get("content"):
            filtered.append({"role": "assistant", "content": message["content"]})
    return filtered[-MAX_MEMORY_MESSAGES:]


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            messages = json.load(f)
        return prune_memory(messages)
    return []


def save_memory(messages):
    pruned = prune_memory(messages)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(pruned, f, indent=2)
