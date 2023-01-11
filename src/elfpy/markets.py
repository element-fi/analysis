"""Market simulators store state information when interfacing AMM pricing models with users"""

from __future__ import annotations  # types will be strings by default in 3.11
from typing import TYPE_CHECKING
import logging

import numpy as np

from elfpy.types import (
    MarketState,
    MarketActionType,
    MarketDeltas,
    StretchedTime,
    Quantity,
    TokenType,
)
from elfpy.wallet import Long, Short, Wallet
import elfpy.utils.time as time_utils
import elfpy.utils.price as price_utils

if TYPE_CHECKING:
    from elfpy.pricing_models.base import PricingModel
    from elfpy.types import MarketAction


class Market:
    """
    Holds state variables for market simulation and executes trades.

    The Market class executes trades by updating market variables according to the given pricing model.
    It also has some helper variables for assessing pricing model values given market conditions.
    """

    def __init__(
        self,
        pricing_model: PricingModel,
        market_state: MarketState = MarketState(
            share_reserves=0,
            bond_reserves=0,
            base_buffer=0,
            bond_buffer=0,
            lp_reserves=0,
            vault_apr=0,
            share_price=1,
            init_share_price=1,
        ),
        position_duration: StretchedTime = StretchedTime(365, 1),
        fee_percent: float = 0,
    ):
        # market state variables
        self.time: float = 0  # t: timefrac unit is time normalized to 1 year, i.e. 0.5 = 1/2 year
        self.pricing_model = pricing_model
        self.market_state: MarketState = market_state
        self.fee_percent: float = fee_percent  # g
        self.position_duration: StretchedTime = position_duration  # how long do positions take to mature

    def check_action_type(self, action_type: MarketActionType, pricing_model_name: str) -> None:
        """Ensure that the agent action is an allowed action for this market

        Arguments
        ---------
        action_type : MarketActionType
            See MarketActionType for all acceptable actions that can be performed on this market
        pricing_model_name : str
            The name of the pricing model, must be "hyperdrive" or "yieldspace"
        """
        if pricing_model_name.lower() == "hyperdrive" or pricing_model_name.lower() == "yieldspace":
            allowed_actions = [
                MarketActionType.OPEN_LONG,
                MarketActionType.CLOSE_LONG,
                MarketActionType.OPEN_SHORT,
                MarketActionType.CLOSE_SHORT,
                MarketActionType.ADD_LIQUIDITY,
                MarketActionType.REMOVE_LIQUIDITY,
            ]
        else:
            raise ValueError(
                "market.check_action_type: ERROR: pricing model name should "
                f'be in ["hyperdrive", "yieldspace"], not {pricing_model_name}'
            )
        if action_type not in allowed_actions:
            raise AssertionError(
                "markets.check_action_type: ERROR: agent_action.action_type should be an allowed action for the"
                f" model={pricing_model_name}, not {action_type}!"
            )

    def trade_and_update(self, agent_action: MarketAction) -> Wallet:
        """
        Execute a trade in the simulated market.

        check which of 6 action types are being executed, and handles each case:
        open_long
        close_long
        open_short
        close_short
        add_liquidity
            pricing model computes new market deltas
            market updates its "liquidity pool" wallet, which stores each trade's mint time and user address
            LP tokens are also stored in user wallet as fungible amounts, for ease of use
        remove_liquidity
            market figures out how much the user has contributed (calcualtes their fee weighting)
            market resolves fees, adds this to the agent_action (optional function, to check AMM logic)
            pricing model computes new market deltas
            market updates its "liquidity pool" wallet, which stores each trade's mint time and user address
            LP tokens are also stored in user wallet as fungible amounts, for ease of use
        """
        self.check_action_type(agent_action.action_type, self.pricing_model.model_name())
        # for each position, specify how to forumulate trade and then execute
        if agent_action.action_type == MarketActionType.OPEN_LONG:  # buy to open long
            market_deltas, agent_deltas = self.open_long(
                wallet_address=agent_action.wallet_address,
                trade_amount=agent_action.trade_amount,
            )
        elif agent_action.action_type == MarketActionType.CLOSE_LONG:  # sell to close long
            market_deltas, agent_deltas = self.close_long(
                wallet_address=agent_action.wallet_address,
                trade_amount=agent_action.trade_amount,
                mint_time=agent_action.mint_time,
            )
        elif agent_action.action_type == MarketActionType.OPEN_SHORT:  # sell PT to open short
            market_deltas, agent_deltas = self.open_short(
                wallet_address=agent_action.wallet_address,
                trade_amount=agent_action.trade_amount,
            )
        elif agent_action.action_type == MarketActionType.CLOSE_SHORT:  # buy PT to close short
            market_deltas, agent_deltas = self.close_short(
                wallet_address=agent_action.wallet_address,
                trade_amount=agent_action.trade_amount,
                mint_time=agent_action.mint_time,
            )
        elif agent_action.action_type == MarketActionType.ADD_LIQUIDITY:
            market_deltas, agent_deltas = self.add_liquidity(
                wallet_address=agent_action.wallet_address,
                trade_amount=agent_action.trade_amount,
            )
        elif agent_action.action_type == MarketActionType.REMOVE_LIQUIDITY:
            market_deltas, agent_deltas = self.remove_liquidity(
                wallet_address=agent_action.wallet_address,
                trade_amount=agent_action.trade_amount,
            )
        else:
            raise ValueError(f'ERROR: Unknown trade type "{agent_action.action_type}".')
        # update market state
        self.update_market(market_deltas)
        logging.info(agent_action)
        logging.debug("market deltas = %s", market_deltas)
        return agent_deltas

    def update_market(self, market_deltas: MarketDeltas) -> None:
        """
        Increments member variables to reflect current market conditions
        """
        for key, value in market_deltas.__dict__.items():
            if value:  # check that it's instantiated and non-empty
                assert np.isfinite(value), f"markets.update_market: ERROR: market delta key {key} is not finite."
        self.market_state.apply_delta(market_deltas)

    # TODO: Use this in the simulator.
    #
    # TODO: Should should_compound be a variable owned by the market?
    def accrue(self, apr: float, delta_time: float, should_compound: bool = True) -> None:
        """Accrues interest to the market

        Arguments
        ---------
        apr : float
            The annualized interest rate during the accrual period.
        delta_time : float
            The amount of time that passed during the accrual period represented
            as a year fraction.
        should_compound : bool
            Indicates whether or not the interest should compound.
        """
        if should_compound:
            price_multiplier = self.market_state.share_price
        else:
            price_multiplier = self.market_state.init_share_price
        self.market_state.share_price += price_multiplier * apr * delta_time

    def tick(self, delta_time: float) -> None:
        """Increments the time member variable"""
        self.time += delta_time

    def open_short(
        self,
        wallet_address: int,
        trade_amount: float,
    ) -> tuple[MarketDeltas, Wallet]:
        """
        take trade spec & turn it into trade details
        compute wallet update spec with specific details
        will be conditional on the pricing model
        """
        # Perform the trade.
        trade_quantity = Quantity(amount=trade_amount, unit=TokenType.PT)
        self.pricing_model.check_input_assertions(
            quantity=trade_quantity,
            market_state=self.market_state,
            fee_percent=self.fee_percent,
            time_remaining=self.position_duration,
        )
        trade_result = self.pricing_model.calc_out_given_in(
            in_=trade_quantity,
            market_state=self.market_state,
            fee_percent=self.fee_percent,
            time_remaining=self.position_duration,
        )
        self.pricing_model.check_output_assertions(trade_result=trade_result)

        # Log the trade result.
        logging.debug("opening short: trade_result = %s", trade_result)

        # Return the market and wallet deltas.
        market_deltas = MarketDeltas(
            d_base_asset=trade_result.market_result.d_base,
            d_token_asset=trade_result.market_result.d_bonds,
            d_bond_buffer=trade_amount,
        )
        max_loss = trade_amount - trade_result.user_result.d_base
        wallet_deltas = Wallet(
            address=wallet_address,
            base=-max_loss,
            # The margin account is seeded with the amount of bonds the trader
            # shorted. As the trader closes out the short, the amount of base
            # that every close operation "costs" will be debited from the
            # margin account. Once the entire balance has been closed, the
            # trader can withdraw the remaining margin balance into their
            # wallet.
            shorts={self.time: Short(balance=trade_amount, margin=trade_amount)},
            fees_paid=trade_result.breakdown.fee,
        )
        return market_deltas, wallet_deltas

    def close_short(
        self,
        wallet_address: int,
        trade_amount: float,
        mint_time: float,
    ) -> tuple[MarketDeltas, Wallet]:
        """
        take trade spec & turn it into trade details
        compute wallet update spec with specific details
            will be conditional on the pricing model
        """

        # Clamp the trade amount to the bond reserves.
        if trade_amount > self.market_state.bond_reserves:
            logging.warning(
                (
                    "markets._close_short: WARNING: trade amount = %g"
                    "is greater than bond reserves = %g."
                    "Adjusting to allowable amount."
                ),
                trade_amount,
                self.market_state.bond_reserves,
            )
            trade_amount = self.market_state.bond_reserves

        # Compute the time remaining given the mint time.
        time_remaining = StretchedTime(
            days=time_utils.get_yearfrac_remaining(self.time, mint_time, self.position_duration.normalized_time) * 365,
            time_stretch=self.position_duration.time_stretch,
        )

        # Perform the trade.
        trade_quantity = Quantity(amount=trade_amount, unit=TokenType.PT)
        self.pricing_model.check_input_assertions(
            quantity=trade_quantity,
            market_state=self.market_state,
            fee_percent=self.fee_percent,
            time_remaining=time_remaining,
        )
        trade_result = self.pricing_model.calc_in_given_out(
            out=trade_quantity,
            market_state=self.market_state,
            fee_percent=self.fee_percent,
            time_remaining=time_remaining,
        )
        self.pricing_model.check_output_assertions(trade_result=trade_result)

        # Log the trade result.
        logging.debug(
            "closing short: trade_result = %s",
            trade_result,
        )

        # Return the market and wallet deltas.
        market_deltas = MarketDeltas(
            d_base_asset=trade_result.market_result.d_base,
            d_token_asset=trade_result.market_result.d_bonds,
            d_bond_buffer=-trade_amount,
        )
        agent_deltas = Wallet(
            address=wallet_address,
            # The short balance will be decreased by the trade amount and the
            # margin account is decreased by the amount of base the trader
            # needed to pay to buy the specified amount of bonds at the current
            # market price.
            shorts={
                mint_time: Short(
                    balance=-trade_amount,
                    margin=trade_result.user_result.d_base,
                )
            },
            fees_paid=trade_result.breakdown.fee,
        )
        return market_deltas, agent_deltas

    def open_long(
        self,
        wallet_address: int,
        trade_amount: float,
    ) -> tuple[MarketDeltas, Wallet]:
        """
        take trade spec & turn it into trade details
        compute wallet update spec with specific details
            will be conditional on the pricing model
        """
        # TODO: Why are we clamping elsewhere but we don't apply the trade at
        # all here?
        if trade_amount <= self.market_state.bond_reserves:
            # Perform the trade.
            trade_quantity = Quantity(amount=trade_amount, unit=TokenType.BASE)
            self.pricing_model.check_input_assertions(
                quantity=trade_quantity,
                market_state=self.market_state,
                fee_percent=self.fee_percent,
                time_remaining=self.position_duration,
            )
            trade_result = self.pricing_model.calc_out_given_in(
                in_=trade_quantity,
                market_state=self.market_state,
                fee_percent=self.fee_percent,
                time_remaining=self.position_duration,
            )
            self.pricing_model.check_output_assertions(trade_result=trade_result)

            # Log the trade result.
            logging.debug(
                "opening long: trade_result %s",
                trade_result,
            )

            # Get the market and wallet deltas to return.
            market_deltas = MarketDeltas(
                d_base_asset=trade_result.market_result.d_base,
                d_token_asset=trade_result.market_result.d_bonds,
                d_base_buffer=trade_result.user_result.d_bonds,
            )
            agent_deltas = Wallet(
                address=wallet_address,
                base=trade_result.user_result.d_base,
                longs={self.time: Long(trade_result.user_result.d_bonds)},
                fees_paid=trade_result.breakdown.fee,
            )
        else:
            market_deltas = MarketDeltas()
            agent_deltas = Wallet(address=wallet_address, base=0)
        return market_deltas, agent_deltas

    def close_long(
        self,
        wallet_address: int,
        trade_amount: float,
        mint_time: float,
    ) -> tuple[MarketDeltas, Wallet]:
        """
        take trade spec & turn it into trade details
        compute wallet update spec with specific details
            will be conditional on the pricing model
        """

        # Compute the time remaining given the mint time.
        time_remaining = StretchedTime(
            days=time_utils.get_yearfrac_remaining(self.time, mint_time, self.position_duration.normalized_time) * 365,
            time_stretch=self.position_duration.time_stretch,
        )

        # Perform the trade.
        trade_quantity = Quantity(amount=trade_amount, unit=TokenType.PT)
        self.pricing_model.check_input_assertions(
            quantity=trade_quantity,
            market_state=self.market_state,
            fee_percent=self.fee_percent,
            time_remaining=time_remaining,
        )
        trade_result = self.pricing_model.calc_out_given_in(
            in_=trade_quantity,
            market_state=self.market_state,
            fee_percent=self.fee_percent,
            time_remaining=time_remaining,
        )
        self.pricing_model.check_output_assertions(trade_result=trade_result)

        # Log the trade result.
        logging.debug("closing long: trade_result = %s", trade_result)

        # Return the market and wallet deltas.
        market_deltas = MarketDeltas(
            d_base_asset=trade_result.market_result.d_base,
            d_token_asset=trade_result.market_result.d_bonds,
            d_base_buffer=-trade_amount,
        )
        agent_deltas = Wallet(
            address=wallet_address,
            base=trade_result.user_result.d_base,
            longs={mint_time: Long(trade_result.user_result.d_bonds)},
            fees_paid=trade_result.breakdown.fee,
        )
        return market_deltas, agent_deltas

    def add_liquidity(
        self,
        wallet_address: int,
        trade_amount: float,
    ) -> tuple[MarketDeltas, Wallet]:
        """
        Computes new deltas for bond & share reserves after liquidity is added
        """
        # get_rate assumes that there is some amount of reserves, and will throw an error if share_reserves is zero
        if (
            self.market_state.share_reserves == 0 and self.market_state.bond_reserves == 0
        ):  # pool has not been initialized
            rate = 0
        else:
            rate = self.rate
        lp_out, d_base_reserves, d_token_reserves = self.pricing_model.calc_lp_out_given_tokens_in(
            d_base=trade_amount,
            rate=rate,
            market_state=self.market_state,
            time_remaining=self.position_duration,
        )
        market_deltas = MarketDeltas(
            d_base_asset=d_base_reserves,
            d_token_asset=d_token_reserves,
            d_lp_reserves=lp_out,
        )
        agent_deltas = Wallet(
            address=wallet_address,
            base=-d_base_reserves,
            lp_tokens=lp_out,
        )
        return market_deltas, agent_deltas

    def remove_liquidity(
        self,
        wallet_address: int,
        trade_amount: float,
    ) -> tuple[MarketDeltas, Wallet]:
        """
        Computes new deltas for bond & share reserves after liquidity is removed
        """
        lp_in, d_base_reserves, d_token_reserves = self.pricing_model.calc_tokens_out_given_lp_in(
            lp_in=trade_amount,
            rate=self.rate,
            market_state=self.market_state,
            time_remaining=self.position_duration,
        )
        market_deltas = MarketDeltas(
            d_base_asset=-d_base_reserves,
            d_token_asset=-d_token_reserves,
            d_lp_reserves=-lp_in,
        )
        agent_deltas = Wallet(
            address=wallet_address,
            base=d_base_reserves,
            lp_tokens=-lp_in,
        )
        return market_deltas, agent_deltas

    @property
    def max_long(self):
        return self.pricing_model.get_max_long(
            market_state=self.market_state, fee_percent=self.fee_percent, time_remaining=self.position_duration
        )

    @property
    def rate(self):
        """Returns the current market apr"""
        # calc_apr_from_spot_price will throw an error if share_reserves <= zero
        # TODO: Negative values should never happen, but do because of rounding errors.
        #       Write checks to remedy this in the market.
        if self.market_state.share_reserves <= 0:  # market is empty; negative value likely due to rounding error
            rate = np.nan
        else:
            rate = price_utils.calc_apr_from_spot_price(self.spot_price, self.position_duration)
        return rate

    @property
    def spot_price(self):
        """Returns the current market price of the share reserves"""
        # calc_spot_price_from_reserves will throw an error if share_reserves is zero
        if self.market_state.share_reserves == 0:  # market is empty
            spot_price = np.nan
        else:
            spot_price = self.pricing_model.calc_spot_price_from_reserves(
                market_state=self.market_state,
                time_remaining=self.position_duration,
            )
        return spot_price

    def get_market_state_string(self) -> str:
        """Returns a formatted string containing all of the Market class member variables"""
        strings = [f"{attribute} = {value}" for attribute, value in self.__dict__.items()]
        state_string = "\n".join(strings)
        return state_string

    def log_market_step_string(self) -> None:
        """Logs the current market step"""
        # TODO: This is a HACK to prevent test_sim from failing on market shutdown
        # when the market closes, the share_reserves are 0 (or negative & close to 0) and several logging steps break
        if self.market_state.share_reserves <= 0:
            spot_price = str(np.nan)
            rate = str(np.nan)
        else:
            spot_price = self.spot_price
            rate = self.rate
        logging.debug(
            (
                "t = %g"
                "\nx = %g"
                "\ny = %g"
                "\nlp = %g"
                "\nz = %g"
                "\nx_b = %g"
                "\ny_b = %g"
                "\np = %s"
                "\npool apr = %s"
            ),
            self.time,
            self.market_state.share_reserves * self.market_state.share_price,
            self.market_state.bond_reserves,
            self.market_state.lp_reserves,
            self.market_state.share_reserves,
            self.market_state.base_buffer,
            self.market_state.bond_buffer,
            str(spot_price),
            str(rate),
        )
