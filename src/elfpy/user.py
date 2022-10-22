"""
Implements abstract classes that control user behavior

TODO: rewrite all functions to have typed inputs
"""

import numpy as np
from scipy.stats import binomtest


class User:
    """
    Implements abstract classes that control user behavior
    """

    def __init__(self, **kwargs):
        """
        Set up initial conditions

        TODO: Like in simulators.py, we want to move away from kwargs for init config.
        """
        self.rng = kwargs["rng"]
        self.verbose = kwargs["verbose"]

    def get_tokens_in_out(self, tokens):
        """Select one of two possible trade directions with some probability"""
        raise NotImplementedError

    def get_trade_amount_usd(self, target_reserves, target_volume, market_price):
        """
        Compute trade amount, which can't be more than the available reserves.

        TODO: Sync with smart contract team & parity their check for maximum trade amount
        """
        trade_mean = target_volume / 10
        trade_std = target_volume / 100
        trade_amount_usd = self.rng.normal(trade_mean, trade_std)
        trade_amount_usd = np.minimum(trade_amount_usd, target_reserves * market_price)
        return trade_amount_usd

    def get_trade(self, market, tokens, trade_direction, target_daily_volume, base_asset_price):
        """Helper function for computing a user trade"""
        (token_in, token_out) = self.get_tokens_in_out(tokens)
        target_reserves = market.get_target_reserves(token_in, trade_direction)
        trade_amount_usd = self.get_trade_amount_usd(
            target_reserves,
            target_daily_volume,
            base_asset_price,
        )
        return (token_in, token_out, trade_amount_usd)


class RandomUser(User):
    """
    Random user that exercises fair behavior
    """

    def get_tokens_in_out(self, tokens):
        """Select one of two possible trade directions with equal probability"""
        direction_index = self.rng.integers(low=0, high=2)  # 0 or 1
        token_in = tokens[direction_index]
        token_out = tokens[1 - direction_index]
        return (token_in, token_out)


class WeightedRandomUser(User):
    """
    Implements abstract classes that control user behavior
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.market = kwargs["market"]
        self.days_remaining = kwargs["days_remaining"]
        self.days_trades = kwargs["days_trades"]
        self.pool_apy_target_range = kwargs["pool_apy_target_range"]
        self.pool_apy_target_range_convergence_speed = kwargs["pool_apy_target_range_convergence_speed"]
        self.run_trade_number = kwargs["run_trade_number"]
        state_keys = [
            "direction_index",
            "apy_distance_in_target_range",
            "apy_distance_from_mid_when_in_range",
            "actual_convergence_strength",
            "expected_proportion",
            "streak_luck",
            "btest",
        ]
        self.user_state = {key: [] for key in state_keys}

    def update_internal_state(
        self, days_remaining, pool_apy_target_range, pool_apy_target_range_convergence_speed, run_trade_number
    ):
        """Updates the internal state"""
        self.days_remaining = days_remaining
        self.pool_apy_target_range = pool_apy_target_range
        self.pool_apy_target_range_convergence_speed = pool_apy_target_range_convergence_speed
        self.run_trade_number = run_trade_number

    def get_tokens_in_out(self, tokens):
        """Select one of two possible trade directions with equal probability"""
        pool_apy = self.market.apy(self.days_remaining)
        direction_index = self.stochastic_direction(pool_apy)
        token_in = tokens[direction_index]
        token_out = tokens[1 - direction_index]
        return (token_in, token_out)

    def stochastic_direction(self, pool_apy):
        """Picks p-value-weighted direction, cutting off tails"""
        # pylint: disable=too-many-arguments
        btest = []
        expected_proportion = 0
        streak_luck = 0
        apy_distance_in_target_range = np.clip(
            (pool_apy - self.pool_apy_target_range[0])
            / (self.pool_apy_target_range[1] - self.pool_apy_target_range[0]),
            0,
            1,
        )
        convergence_direction = (
            0 if apy_distance_in_target_range > 0.5 else 1
        )  # if you're above the midpoint of the targe range
        apy_distance_from_mid_when_in_range = np.clip(
            np.abs(apy_distance_in_target_range - 0.5) * 2, 0, 1
        )  # 0 if you're at the midpoint, 1 if you're at the edge
        actual_convergence_strength = (
            0.5 + (self.pool_apy_target_range_convergence_speed - 0.5) * apy_distance_from_mid_when_in_range
        )  # pool_apy_target_range_convergence_speed at edge or outside, scales to 0 at midpoint
        expected_proportion = (
            actual_convergence_strength if convergence_direction == 1 else 1 - actual_convergence_strength
        )
        if len(self.days_trades) > 0:
            btest = binomtest(
                k=sum(self.days_trades),
                n=len(self.days_trades),
                p=expected_proportion,
            )
            streak_luck = 1 - btest.pvalue
        if self.verbose and streak_luck > 0.98:
            direction_index = 1 - round(sum(self.days_trades) / len(self.days_trades))
            print(
                "trade"
                f" {self.run_trade_number}"
                f" days_trades={self.days_trades}+{direction_index}k={sum(self.days_trades)}"
                f" n={len(self.days_trades)} ratio={sum(self.days_trades)/len(self.days_trades)}"
                f" streak_luck: {streak_luck}"
            )
        else:
            if 0 < apy_distance_from_mid_when_in_range < 1:
                actual_convergence_strength = (
                    actual_convergence_strength + (1 - actual_convergence_strength) * streak_luck**1.5
                )  # force convergence when on bad streaks
            direction_index = (
                convergence_direction if self.rng.random() < actual_convergence_strength else 1 - convergence_direction
            )
        self.days_trades.append(direction_index)
        if self.verbose and pool_apy > 0.2:
            print(
                "trade"
                + f" {self.run_trade_number}"
                + f" days_trades={self.days_trades}"
                + f" k={sum(self.days_trades)}"
                + f" n={len(self.days_trades)}"
                + f" ratio={sum(self.days_trades)/len(self.days_trades)}"
                + f" streak_luck: {streak_luck}"
            )
            if self.pool_apy_target_range is not None:
                print(btest)
                print(f"expected_proportion={expected_proportion}")
                print(
                    f"trade {self.run_trade_number} pool_apy"
                    + f" = {pool_apy:,.4%} apy_distance_in_target_range ="
                    + f" {apy_distance_in_target_range},"
                    + " apy_distance_from_mid_when_in_range ="
                    + f" {apy_distance_from_mid_when_in_range},"
                    + " actual_convergence_strength ="
                    + f" {actual_convergence_strength}, direction_index ="
                    + f" {direction_index}"
                )
        # Append new values the internal user state
        self.user_state["direction_index"].append(direction_index)
        self.user_state["apy_distance_in_target_range"].append(apy_distance_in_target_range)
        self.user_state["apy_distance_from_mid_when_in_range"].append(apy_distance_from_mid_when_in_range)
        self.user_state["actual_convergence_strength"].append(actual_convergence_strength)
        self.user_state["expected_proportion"].append(expected_proportion)
        self.user_state["streak_luck"].append(streak_luck)
        self.user_state["btest"].append(btest)
        return direction_index
