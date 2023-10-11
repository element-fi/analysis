"""Policies for expert system trading bots"""
from __future__ import annotations

from typing import NamedTuple

# Actual policies
from .random_agent import RandomAgent
from .arbitrage import ArbitragePolicy


# Container for all the policies
class Zoo(NamedTuple):
    """All policies in agent0."""

    random_agent = RandomAgent
    arbitrage_policy = ArbitragePolicy

    def describe(self, policies: list | str | None = None) -> str:
        """Describe policies, either specific ones provided, or all of them."""
        # programmatically create a list with all the policies
        existing_policies = [
            attr for attr in dir(self) if not attr.startswith("_") and attr not in ["describe", "count", "index"]
        ]
        if policies is None:  # we are not provided specific policies to describe
            policies = existing_policies
        elif not isinstance(policies, list):  # not a list
            policies = [policies]  # we make it a list

        for policy in policies:
            if policy not in existing_policies:
                raise ValueError(f"Unknown policy: {policy}")

        return "\n".join([f"=== {policy} ===\n{getattr(self, policy).description()}" for policy in policies])
