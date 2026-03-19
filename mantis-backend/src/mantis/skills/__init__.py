"""
M.A.N.T.I.S. — Skill Interface
Abstract base class that all skills implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Skill(ABC):
    """
    Base interface for all M.A.N.T.I.S. skills.

    Every skill must implement:
      - collect()  → pull current data from this skill's sources
      - execute()  → perform an action (optional; only for action-capable skills)
    """

    name: str = "base"
    version: str = "0.0.0"
    enabled: bool = True

    @abstractmethod
    async def collect(self) -> Any:
        """Pull current data from this skill's data sources."""
        ...

    async def execute(self, params: dict) -> Any:
        """Perform an action. Override in action-capable skills."""
        raise NotImplementedError(f"Skill '{self.name}' does not support execute()")
