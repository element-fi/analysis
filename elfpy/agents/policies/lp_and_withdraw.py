"""User strategy that adds liquidity and then removes it when enough time has passed"""
from __future__ import annotations

from numpy.random._generator import Generator as NumpyGenerator

from elfpy.agents.agent import Agent
from elfpy.markets.hyperdrive.hyperdrive_actions import HyperdriveMarketAction, MarketActionType
from elfpy.markets.hyperdrive.hyperdrive_market import Market as HyperdriveMarket
from elfpy.math import FixedPoint
from elfpy.types import Trade, MarketType

# pylint: disable=too-many-arguments


class LpAndWithdrawAgent(Agent):
    """
    simple LP
    only has one LP open at a time
    """

    def __init__(
        self,
        wallet_address: int,
        budget: FixedPoint = FixedPoint("1000.0"),
        rng: NumpyGenerator | None = None,
        amount_to_lp: FixedPoint = FixedPoint("100.0"),
        time_to_withdraw: FixedPoint = FixedPoint("1.0"),
    ):
        """call basic policy init then add custom stuff"""
        self.amount_to_lp = amount_to_lp
        self.time_to_withdraw = time_to_withdraw
        super().__init__(wallet_address, budget, rng)

    def action(self, market: HyperdriveMarket) -> list[Trade]:
        """
        implement user strategy
        LP if you can, but only do it once
        """
        # pylint disable=unused-argument
        action_list: list[Trade] = []
        has_lp = self.wallet.lp_tokens > FixedPoint(0)
        amount_in_base = self.wallet.balance.amount
        can_lp = amount_in_base >= self.amount_to_lp
        if not has_lp and can_lp:
            action_list.append(
                Trade(
                    market=MarketType.HYPERDRIVE,
                    trade=HyperdriveMarketAction(
                        action_type=MarketActionType.ADD_LIQUIDITY,
                        trade_amount=self.amount_to_lp,
                        wallet=self.wallet,
                    ),
                )
            )
        elif has_lp:
            enough_time_has_passed = market.block_time.time > self.time_to_withdraw
            if enough_time_has_passed:
                action_list.append(
                    Trade(
                        market=MarketType.HYPERDRIVE,
                        trade=HyperdriveMarketAction(
                            action_type=MarketActionType.REMOVE_LIQUIDITY,
                            trade_amount=self.wallet.lp_tokens,
                            wallet=self.wallet,
                        ),
                    )
                )
        return action_list
