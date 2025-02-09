from dataclasses import dataclass, field
from typing import List, Dict, Optional
import ollama
from enum import Enum, auto
import subprocess


class MessageLength(Enum):
    CONCISE = "concise"
    BALANCED = "balanced"
    DETAILED = "detailed"


@dataclass
class Message:
    role: str
    content: str


@dataclass
class Participant:
    name: str
    model: str
    history: List[Message] = field(default_factory=list)

    def __post_init__(self):
        try:
            # First try using ollama CLI to validate
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                available_models = []
                for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                    if line.strip():
                        model_name = line.split()[0]
                        available_models.append(model_name)

                if self.model not in available_models:
                    raise ValueError(f"Model '{self.model}' not found in available models: {available_models}")
            else:
                # Fallback to API check
                ollama.show(model=self.model)

        except Exception as e:
            raise ValueError(f"Could not validate model {self.model}: {str(e)}")


class ConversationConfig:
    def __init__(
            self,
            topic: str,
            num_turns: int,
            message_style: MessageLength,
            participants: List[Participant]
    ):
        if num_turns < 1:
            raise ValueError("Number of turns must be positive")
        if len(participants) < 2:
            raise ValueError("Need at least 2 participants")

        self.topic = topic
        self.num_turns = num_turns
        self.message_style = message_style
        self.participants = participants
