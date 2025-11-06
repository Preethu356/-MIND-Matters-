# helpers.py
# Additional utility functions that can be imported by app.py

from typing import List, Dict

def format_message(role: str, content: str) -> Dict[str, str]:
    return {"role": role, "content": content}

def sample_grounding_exercise() -> List[str]:
    return [
        "Name 5 things you can see right now.",
        "Name 4 things you can touch.",
        "Name 3 things you can hear.",
        "Name 2 things you can smell (or would like to).",
        "Name 1 thing about yourself that you like."
    ]
