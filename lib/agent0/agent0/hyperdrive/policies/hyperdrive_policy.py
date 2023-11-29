"""Base class for hyperdrive policies"""

from ethpy.hyperdrive.api import HyperdriveInterface

from agent0.base import Trade
from agent0.base.policies import BasePolicy
from agent0.hyperdrive.state import HyperdriveMarketAction, HyperdriveWallet


class HyperdrivePolicy(BasePolicy[HyperdriveInterface, HyperdriveWallet]):
    """Hyperdrive policy."""

    def action(
        self, interface: HyperdriveInterface, wallet: HyperdriveWallet
    ) -> tuple[list[Trade[HyperdriveMarketAction]], bool]:
        """Returns an empty list, indicating no action.

        Arguments
        ---------
        interface: HyperdriveInterface
            Interface for the market on which this agent will be executing trades (MarketActions).
        wallet: HyperdriveWallet
            The agent's wallet.

        Returns
        -------
        tuple[list[MarketAction], bool]
            A tuple where the first element is a list of actions,
            and the second element defines if the agent is done trading.
        """
        raise NotImplementedError
