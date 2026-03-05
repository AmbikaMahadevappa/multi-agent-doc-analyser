"""
Base Agent
===========
All agents inherit from this class. Handles OpenAI API calls,
message bus interaction, and shared utilities.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from openai import OpenAI
from agents.message_bus import MessageBus, Message
from utils.logger import get_logger


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the pipeline.

    Each agent has:
      - A name (used for message routing)
      - Access to the shared message bus
      - Access to the OpenAI client
      - A system prompt defining its role and behaviour
    """

    def __init__(
        self,
        name: str,
        model: str,
        message_bus: MessageBus,
        verbose: bool = False
    ):
        self.name = name
        self.model = model
        self.bus = message_bus
        self.verbose = verbose
        self.logger = get_logger(name)
        self.client = OpenAI()  # reads OPENAI_API_KEY from environment

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Each agent defines its own role and behaviour."""
        pass

    def call_llm(
        self,
        user_message: str,
        temperature: float = 0.2,
        max_tokens: int = 1500,
        extra_messages: Optional[List[Dict]] = None
    ) -> str:
        """
        Call the OpenAI API with this agent's system prompt.
        Returns the response text.
        """
        messages = [{"role": "system", "content": self.system_prompt}]

        if extra_messages:
            messages.extend(extra_messages)

        messages.append({"role": "user", "content": user_message})

        if self.verbose:
            self.logger.info(f"[{self.name}] Calling {self.model}...")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        result = response.choices[0].message.content.strip()

        if self.verbose:
            self.logger.info(f"[{self.name}] Response received ({len(result)} chars)")

        return result

    def publish(self, recipient: str, message_type: str, content: Any) -> None:
        """Publish a message to another agent via the bus."""
        self.bus.publish(Message(
            sender=self.name,
            recipient=recipient,
            message_type=message_type,
            content=content
        ))

    def receive(self) -> List[Message]:
        """Read all pending messages addressed to this agent."""
        return self.bus.receive(self.name)

    @abstractmethod
    def run(self, **kwargs) -> Any:
        """Execute this agent's primary task."""
        pass
