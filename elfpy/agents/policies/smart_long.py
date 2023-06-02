"""Agent policy for leveraged long positions"""
from __future__ import annotations

from numpy.random._generator import Generator as NumpyGenerator

from elfpy import WEI
from elfpy.agents.agent import Agent
from elfpy.markets.hyperdrive.hyperdrive_market import Market as HyperdriveMarket
from elfpy.markets.hyperdrive.hyperdrive_actions import HyperdriveMarketAction, MarketActionType
from elfpy.math import FixedPoint, FixedPointMath
from elfpy.types import Trade, MarketType

# pylint: disable=too-many-arguments


class LongLouie(Agent):
    """Agent that opens longs to push the fixed-rate towards the variable-rate

    .. note::
        My strategy:
            - I'm not willing to open a long if it will cause the fixed-rate apr to go below the variable rate
                - I simulate the outcome of my trade, and only execute on this condition
            - I only close if the position has matured
            - I have total budget of 2k -> 250k (gauss mean=75k; std=50k, i.e. 68% values are within 75k +/- 50k)
            - I only open one long at a time

    """

    def __init__(
        self,
        wallet_address: int,
        budget: FixedPoint,
        rng: NumpyGenerator,
        trade_chance: FixedPoint,
        risk_threshold: FixedPoint,
    ) -> None:
        """Add custom stuff then call basic policy init"""
        self.trade_chance = trade_chance
        self.risk_threshold = risk_threshold
        super().__init__(wallet_address, budget, rng)
        self.rng: NumpyGenerator = rng  # TODO: Figure out a better way to narrow this type

    def action(self, market: HyperdriveMarket) -> list[Trade]:
        """Implement a Long Louie user strategy

        Parameters
        ----------
        market : Market
            the trading market

        Returns
        -------
        action_list : list[MarketAction]
        """
        # Any trading at all is based on a weighted coin flip -- they have a trade_chance% chance of executing a trade
        gonna_trade = self.rng.choice([True, False], p=[float(self.trade_chance), 1 - float(self.trade_chance)])
        if not gonna_trade:
            return []
        action_list = []
        for long_time in self.wallet.longs:  # loop over longs # pylint: disable=consider-using-dict-items
            # if any long is mature
            if (market.block_time.time - FixedPoint(long_time)) >= market.annualized_position_duration:
                trade_amount = self.wallet.longs[long_time].balance  # close the whole thing
                action_list += [
                    Trade(
                        market=MarketType.HYPERDRIVE,
                        trade=HyperdriveMarketAction(
                            action_type=MarketActionType.CLOSE_LONG,
                            trade_amount=trade_amount,
                            wallet=self.wallet,
                            mint_time=long_time,
                        ),
                    )
                ]
        long_balances = [long.balance for long in self.wallet.longs.values()]
        has_opened_long = bool(any(long_balance > 0 for long_balance in long_balances))
        # only open a long if the fixed rate is higher than variable rate
        if (market.fixed_apr - market.market_state.variable_apr) > self.risk_threshold and not has_opened_long:
            total_bonds_to_match_variable_apr = market.pricing_model.calc_bond_reserves(
                target_apr=market.market_state.variable_apr,  # fixed rate targets the variable rate
                time_remaining=market.position_duration,
                market_state=market.market_state,
            )
            # get the delta bond amount & convert units
            new_bonds_to_match_variable_apr = (
                market.market_state.bond_reserves - total_bonds_to_match_variable_apr
            ) * market.spot_price
            # divide by 2 to adjust for changes in share reserves when the trade is executed
            adjusted_bonds = new_bonds_to_match_variable_apr / FixedPoint(2.0)
            # get the maximum amount the agent can long given the market and the agent's wallet
            max_trade_amount = self.get_max_long(market)
            # don't want to trade more than the agent has or more than the market can handle
            trade_amount = FixedPointMath.minimum(max_trade_amount, adjusted_bonds)
            # TODO: This is a hack until we fix get_max
            # issue #440
            trade_amount = trade_amount / FixedPoint("100.0")
            if trade_amount > WEI:
                action_list += [
                    Trade(
                        market=MarketType.HYPERDRIVE,
                        trade=HyperdriveMarketAction(
                            action_type=MarketActionType.OPEN_LONG,
                            trade_amount=trade_amount,
                            wallet=self.wallet,
                            mint_time=market.block_time.time,
                        ),
                    )
                ]
        return action_list
