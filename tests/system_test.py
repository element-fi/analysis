"""System test for end to end testing of elf-simulations"""
import logging
from decimal import Decimal
from typing import Type

import pandas as pd
from agent0 import build_account_key_config_from_agent_config
from agent0.base.config import AgentConfig, EnvironmentConfig
from agent0.base.policies import BasePolicy
from agent0.hyperdrive.exec import run_agents
from chainsync.db.hyperdrive.interface import get_pool_config
from chainsync.exec import acquire_data
from ethpy import EthConfig
from ethpy.hyperdrive import HyperdriveAddresses
from ethpy.test_fixtures.deploy_hyperdrive import _calculateTimeStretch
from fixedpointmath import FixedPoint
from sqlalchemy.orm import Session

# This pass is to prevent auto reordering imports from reordering the imports below
pass  # pylint: disable=unnecessary-pass

# Test fixture imports
# Ignoring unused import warning, fixtures are used through variable name
from agent0.test_fixtures import (  # pylint: disable=unused-import, ungrouped-imports
    AgentDoneException,
    cycle_trade_policy,
)
from chainsync.test_fixtures import db_session  # pylint: disable=unused-import
from ethpy.test_fixtures import (  # pylint: disable=unused-import, ungrouped-imports
    hyperdrive_contract_addresses,
    local_chain,
)

# fixture arguments in test function have to be the same as the fixture name
# pylint: disable=redefined-outer-name


class TestLocalChain:
    """Tests bringing up local chain"""

    # This is using 2 fixtures. Since hyperdrive_contract_address depends on local_chain, we need both here
    # This is due to adding test fixtures through imports
    def test_hyperdrive_init_and_deploy(self, local_chain: str, hyperdrive_contract_addresses: HyperdriveAddresses):
        """Create and entry"""
        print(local_chain)
        print(hyperdrive_contract_addresses)


def _to_unscaled_decimal(scaled_value: int) -> Decimal:
    return Decimal(str(FixedPoint(scaled_value=scaled_value)))


class TestBotToDb:
    """Tests pipeline from bots making trades to viewing the trades in the db"""

    # This is using 3 fixtures
    def test_bot_to_db(
        self,
        local_chain: str,
        hyperdrive_contract_addresses: HyperdriveAddresses,
        cycle_trade_policy: Type[BasePolicy],
        db_session: Session,
    ):
        # Build environment config
        env_config = EnvironmentConfig(
            delete_previous_logs=False,
            halt_on_errors=True,
            log_filename="system_test",
            log_level=logging.INFO,
            log_stdout=True,
            random_seed=1234,
            username="test",
        )

        # Build agent config
        agent_config: list[AgentConfig] = [
            AgentConfig(
                policy=cycle_trade_policy,
                number_of_agents=1,
                slippage_tolerance=FixedPoint(0.0001),
                base_budget_wei=int(10_000e18),  # 10k base
                eth_budget_wei=int(10e18),  # 10 base
                init_kwargs={"static_trade_amount_wei": int(100e18)},  # 100 base static trades
            ),
        ]

        # No need for random seed, this bot is deterministic
        account_key_config = build_account_key_config_from_agent_config(agent_config)

        # Build custom eth config pointing to local chain
        eth_config = EthConfig(
            # Artifacts_url isn't used here, as we explicitly set addresses and passed to run_bots
            ARTIFACTS_URL="not_used",
            RPC_URL=local_chain,
            # Using default abi dir
        )

        # Run bots
        try:
            run_agents(
                env_config,
                agent_config,
                account_key_config,
                develop=True,
                eth_config=eth_config,
                contract_addresses=hyperdrive_contract_addresses,
            )
        except AgentDoneException:
            # Using this exception to stop the agents,
            # so this exception is expected on test pass
            pass

        # Run acquire data to get data from chain to db in subprocess
        acquire_data(
            start_block=8,  # First 7 blocks are deploying hyperdrive, ignore
            eth_config=eth_config,
            db_session=db_session,
            contract_addresses=hyperdrive_contract_addresses,
            # Exit the script after catching up to the chain
            exit_on_catch_up=True,
        )

        # Run acquire data to get data from chain to db in subprocess
        acquire_data(
            start_block=8,  # First 7 blocks are deploying hyperdrive, ignore
            eth_config=eth_config,
            db_session=db_session,
            contract_addresses=hyperdrive_contract_addresses,
            # Exit the script after catching up to the chain
            exit_on_catch_up=True,
        )

        # Test db entries are what we expect
        # We don't coerce to float because we want exact values in decimal
        db_pool_config = get_pool_config(db_session, coerce_float=False)

        # TODO these expected values are defined in lib/ethpy/ethpy/test_fixtures/deploy_hyperdrive.py
        # Eventually, we want to parameterize these values to pass into deploying hyperdrive
        expected_timestretch_fp = FixedPoint(scaled_value=_calculateTimeStretch(int(0.05e18)))
        # TODO this is actually inv of solidity time stretch, fix
        expected_timestretch = _to_unscaled_decimal((1 / expected_timestretch_fp).scaled_value)
        expected_inv_timestretch = _to_unscaled_decimal(expected_timestretch_fp.scaled_value)

        expected_pool_config = pd.Series(
            {
                "contractAddress": hyperdrive_contract_addresses.mock_hyperdrive,
                "baseToken": hyperdrive_contract_addresses.base_token,
                "initialSharePrice": _to_unscaled_decimal(int(1e18)),
                "minimumShareReserves": _to_unscaled_decimal(int(10e18)),
                "positionDuration": 604800,  # 1 week
                "checkpointDuration": 3600,  # 1 hour
                # TODO this is actually inv of solidity time stretch, fix
                "timeStretch": expected_timestretch,
                # "governance":
                # "feeCollector":
                "invTimeStretch": expected_timestretch,
            }
        )

        # TODO timestretch has rounding error

        # Ensure all trades are in the db
