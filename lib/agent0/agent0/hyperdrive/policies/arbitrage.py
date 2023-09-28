"""Agent policy for smart short positions"""
from __future__ import annotations

from typing import TYPE_CHECKING

from agent0.hyperdrive.state import HyperdriveActionType, HyperdriveMarketAction
from elfpy.types import MarketType, Trade
from fixedpointmath import FixedPoint

from .hyperdrive_policy import HyperdrivePolicy

if TYPE_CHECKING:
    from agent0.hyperdrive.state import HyperdriveWallet
    from ethpy.hyperdrive import HyperdriveInterface
    from numpy.random._generator import Generator as NumpyGenerator


class ArbitragePolicy(HyperdrivePolicy):
    """Agent that arbitrages based on the fixed rate

    .. note::
        My strategy:
            - I arbitrage the fixed rate percentage based on thresholds
            - I always close any matured open positions
            - If the fixed rate is higher than `high_fixed_rate_thresh`,
                I close all open shorts an open a new long for `trade_amount` base
            - If the fixed rate is lower than `low_fixed_rate_thresh`,
                I close all open longs and open a new short for `trade_amount` bonds
    """

    def __init__(
        self,
        budget: FixedPoint,
        rng: NumpyGenerator | None = None,
        slippage_tolerance: FixedPoint | None = None,
        trade_amount: FixedPoint | None = None,
        high_fixed_rate_thresh: FixedPoint | None = None,
        low_fixed_rate_thresh: FixedPoint | None = None,
    ):
        """Initializes the bot

        Arguments
        ---------
        budget: FixedPoint
            The budget of this policy
        rng: NumpyGenerator | None
            Random number generator
        slippage_tolerance: FixedPoint | None
            Slippage tolerance of trades
        trade_amount: FixedPoint | None
            The static amount to trade when opening a position
        high_fixed_rate_thresh: FixedPoint | None
            The upper threshold of the fixed rate to open a position
        low_fixed_rate_thresh: FixedPoint | None
            The lower threshold of the fixed rate to open a position
        """

        # Defaults
        if trade_amount is None:
            trade_amount = FixedPoint(100)
        if high_fixed_rate_thresh is None:
            high_fixed_rate_thresh = FixedPoint(0.1)
        if low_fixed_rate_thresh is None:
            low_fixed_rate_thresh = FixedPoint(0.02)
        self.trade_amount = trade_amount
        self.high_fixed_rate_thresh = high_fixed_rate_thresh
        self.low_fixed_rate_thresh = low_fixed_rate_thresh

        super().__init__(budget, rng, slippage_tolerance)

    def action(self, interface: HyperdriveInterface, wallet: HyperdriveWallet) -> list[Trade[HyperdriveMarketAction]]:
        """Specify actions.

        Arguments
        ---------
        market : HyperdriveMarketState
            the trading market
        wallet : HyperdriveWallet
            agent's wallet

        Returns
        -------
        list[Trade]
            list of actions
        """
        # Get fixed rate
        # TODO currently calculating fixed rate, but we should be getting it from the interface
        # fixed_rate = interface.fixed_rate
        pool_config = interface.pool_config
        pool_info = interface.pool_info
        init_share_price = pool_config["initialSharePrice"]
        share_reserves = pool_info["shareReserves"]
        bond_reserves = pool_info["bondReserves"]
        time_stretch = pool_config["timeStretch"]
        annualized_time = interface.position_duration_in_years
        spot_price = ((init_share_price * share_reserves) / bond_reserves) ** time_stretch
        fixed_rate = (1 - spot_price) / (spot_price * annualized_time)

        action_list = []

        # Close longs if matured
        for maturity_time, long in wallet.longs.items():
            # If matured
            if maturity_time >= interface.current_block_time:
                action_list.append(
                    Trade(
                        market_type=MarketType.HYPERDRIVE,
                        market_action=HyperdriveMarketAction(
                            action_type=HyperdriveActionType.CLOSE_LONG,
                            trade_amount=long.balance,
                            wallet=wallet,
                            maturity_time=maturity_time,
                        ),
                    )
                )
        # Close shorts if matured
        for maturity_time, short in wallet.shorts.items():
            # If matured
            if maturity_time >= interface.current_block_time:
                action_list.append(
                    Trade(
                        market_type=MarketType.HYPERDRIVE,
                        market_action=HyperdriveMarketAction(
                            action_type=HyperdriveActionType.CLOSE_LONG,
                            trade_amount=short.balance,
                            wallet=wallet,
                            maturity_time=maturity_time,
                        ),
                    )
                )

        # High fixed rate detected
        if fixed_rate >= self.high_fixed_rate_thresh:
            # Close all open shorts
            if len(wallet.shorts) > 0:
                for maturity_time, short in wallet.shorts.items():
                    action_list.append(
                        Trade(
                            market_type=MarketType.HYPERDRIVE,
                            market_action=HyperdriveMarketAction(
                                action_type=HyperdriveActionType.CLOSE_SHORT,
                                trade_amount=short.balance,
                                wallet=wallet,
                                maturity_time=maturity_time,
                            ),
                        )
                    )
            # Open a new long
            action_list.append(
                Trade(
                    market_type=MarketType.HYPERDRIVE,
                    market_action=HyperdriveMarketAction(
                        action_type=HyperdriveActionType.OPEN_LONG,
                        trade_amount=self.trade_amount,
                        wallet=wallet,
                    ),
                )
            )

        # Low fixed rate detected
        if fixed_rate <= self.low_fixed_rate_thresh:
            # Close all open longs
            if len(wallet.longs) > 0:
                for maturity_time, long in wallet.longs.items():
                    action_list.append(
                        Trade(
                            market_type=MarketType.HYPERDRIVE,
                            market_action=HyperdriveMarketAction(
                                action_type=HyperdriveActionType.CLOSE_LONG,
                                trade_amount=long.balance,
                                wallet=wallet,
                                maturity_time=maturity_time,
                            ),
                        )
                    )
            # Open a new short
            action_list.append(
                Trade(
                    market_type=MarketType.HYPERDRIVE,
                    market_action=HyperdriveMarketAction(
                        action_type=HyperdriveActionType.OPEN_SHORT,
                        trade_amount=self.trade_amount,
                        wallet=wallet,
                    ),
                )
            )

        return action_list
