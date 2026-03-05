"""
Message Bus — Agent Communication Layer
========================================
Implements an asynchronous-style message passing system between agents.
Each agent publishes messages to the bus; other agents can read from it.
This mirrors A2A (Agent-to-Agent) communication patterns used in
production multi-agent systems.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Message:
    """A single message passed between agents."""
    sender: str
    recipient: str
    message_type: str          # e.g. "task", "result", "error", "status"
    content: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)

    def __repr__(self):
        return (
            f"Message(from={self.sender!r}, to={self.recipient!r}, "
            f"type={self.message_type!r}, ts={self.timestamp})"
        )


class MessageBus:
    """
    Central message bus for inter-agent communication.

    Agents publish messages here. The orchestrator reads and routes them.
    This decouples agents from each other — no agent holds a direct
    reference to another, they only communicate through the bus.
    """

    def __init__(self, verbose: bool = False):
        self._inbox: Dict[str, List[Message]] = {}
        self._all_messages: List[Message] = []
        self.verbose = verbose

    def publish(self, message: Message) -> None:
        """Publish a message to the bus, routing it to the recipient's inbox."""
        if message.recipient not in self._inbox:
            self._inbox[message.recipient] = []

        self._inbox[message.recipient].append(message)
        self._all_messages.append(message)

        if self.verbose:
            logger.info(
                f"[BUS] {message.sender} → {message.recipient} "
                f"[{message.message_type}]"
            )

    def receive(self, agent_name: str) -> List[Message]:
        """Retrieve and clear all pending messages for a given agent."""
        messages = self._inbox.get(agent_name, [])
        self._inbox[agent_name] = []
        return messages

    def peek(self, agent_name: str) -> List[Message]:
        """Read messages without clearing them."""
        return self._inbox.get(agent_name, [])

    def get_history(self) -> List[Message]:
        """Return the full communication history."""
        return self._all_messages.copy()

    def get_history_summary(self) -> List[Dict]:
        """Return a human-readable summary of all messages."""
        return [
            {
                "timestamp": m.timestamp,
                "from": m.sender,
                "to": m.recipient,
                "type": m.message_type,
                "preview": str(m.content)[:120] + "..." if len(str(m.content)) > 120 else str(m.content)
            }
            for m in self._all_messages
        ]
