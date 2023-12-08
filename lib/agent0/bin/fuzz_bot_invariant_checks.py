"""Script for checking Hyperdrive invariants at each block."""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import asdict
from math import isclose
from typing import NamedTuple, Sequence

from eth_typing import BlockNumber
from ethpy import build_eth_config
from ethpy.hyperdrive.interface import HyperdriveInterface
from fixedpointmath import FixedPoint
from hexbytes import HexBytes
from hyperlogs import ExtendedJSONEncoder, setup_logging
from web3.types import BlockData

from agent0.base.config import EnvironmentConfig


def main(argv: Sequence[str] | None = None) -> None:
    """Check Hyperdrive invariants each block.

    Arguments
    ---------
    argv: Sequence[str]
        A sequnce containing the uri to the database server and the test epsilon.
    """
    # Setup the experiment
    parsed_args, interface = setup_fuzz(argv)
    # Run the loop forever
    last_executed_block_number = 0  # no matter what we will run the check the first time
    while True:
        latest_block = interface.get_block("latest")
        latest_block_number = latest_block.get("number", None)
        if latest_block_number is None:
            raise AssertionError("Block has no number.")
        if not latest_block_number > last_executed_block_number:
            # take a nap
            time.sleep(parsed_args.sleep_time)
            continue
        # Update block number
        last_executed_block_number = latest_block_number
        run_invariant_checks(latest_block, latest_block_number, interface, parsed_args.test_epsilon)


def setup_fuzz(argv: Sequence[str] | None) -> tuple[Args, HyperdriveInterface]:
    """Setup the fuzz config & interface.

    Arguments
    ---------
    argv: Sequence[str]
        A sequnce containing the uri to the database server and the test epsilon.

    Returns
    -------
    tuple[Args, HyperdriveInterface]
        The parsed arguments and interface constructed from those arguments.
    """
    parsed_args = parse_arguments(argv)
    eth_config = build_eth_config(parsed_args.eth_config_env_file)
    env_config = EnvironmentConfig(
        delete_previous_logs=False,
        halt_on_errors=False,
        log_filename=".logging/invariant_checks.log",
        log_level=logging.ERROR,
        log_stdout=False,
        global_random_seed=1234,
        username="INVARIANT_CHECKS",
    )
    # Setup logging
    setup_logging(
        log_filename=env_config.log_filename,
        max_bytes=env_config.max_bytes,
        log_level=env_config.log_level,
        delete_previous_logs=env_config.delete_previous_logs,
        log_stdout=env_config.log_stdout,
        log_format_string=env_config.log_formatter,
    )
    # Setup hyperdrive interface
    interface = HyperdriveInterface(eth_config)
    return parsed_args, interface


def run_invariant_checks(
    latest_block: BlockData,
    latest_block_number: BlockNumber,
    interface: HyperdriveInterface,
    test_epsilon: float,
) -> None:
    """Run the invariant checks.

    Arguments
    ---------
    latest_block: BlockData
        The current block to be tested.
    latest_block_number: BlockNumber
        The current block number.
    interface: HyperdriveInterface
        An instantiated HyperdriveInterface object constructed using the script arguments.
    test_epsilon: float
        The tolerance for the invariance checks.
    """
    # Get the variables to check
    pool_state = interface.get_hyperdrive_state(latest_block)
    epsilon = FixedPoint(str(test_epsilon))

    # Check each invariant
    failed = False

    # Hyperdrive base & eth balances should always be zero
    if pool_state.hyperdrive_base_balance != FixedPoint(0):
        logging.critical(
            "hyperdrive_base_balance=%s != 0. Test failed at block %s",
            pool_state.hyperdrive_base_balance,
            latest_block_number,
        )
        failed = True
    if pool_state.hyperdrive_eth_balance != FixedPoint(0):
        logging.critical(
            "hyperdrive_eth_balance=%s != 0. Test failed at block %s",
            pool_state.hyperdrive_eth_balance,
            latest_block_number,
        )
        failed = True

    # Total shares is correctly calculated
    if not isclose(
        pool_state.vault_shares,
        pool_state.pool_info.share_reserves
        + pool_state.pool_info.shorts_outstanding / pool_state.pool_info.share_price
        + pool_state.gov_fees_accrued
        + pool_state.pool_info.withdrawal_shares_proceeds,
        abs_tol=epsilon,
    ):
        logging.critical(
            "total_shares=%s is incorrect, should be %s. Test failed at block %s.",
            pool_state.vault_shares,
            pool_state.pool_info.share_reserves
            + pool_state.pool_info.shorts_outstanding / pool_state.pool_info.share_price
            + pool_state.gov_fees_accrued
            + pool_state.pool_info.withdrawal_shares_proceeds,
            latest_block_number,
        )
        failed = True

    # The system should always be solvent
    solvency = (
        pool_state.pool_info.share_reserves
        - pool_state.pool_info.long_exposure
        - pool_state.pool_config.minimum_share_reserves
    )
    if not isclose(solvency, FixedPoint(0), abs_tol=epsilon):
        logging.critical(
            "solvency=share_reserves - global_exposure - minimum_share_reserves=%s != 0. Test failed at block %s",
            solvency,
            latest_block_number,
        )
        failed = True

    # The pool has more than the minimum share reserves
    if not isclose(
        pool_state.pool_config.minimum_share_reserves,
        pool_state.pool_info.share_reserves * pool_state.pool_info.share_price - pool_state.pool_info.long_exposure,
        abs_tol=epsilon,
    ):
        logging.critical(
            (
                "minimum_share_reserves=%s != share_reserves * share_price - global_exposure = %s. "
                "Test failed at block %s"
            ),
            pool_state.pool_config.minimum_share_reserves,
            pool_state.pool_info.share_reserves * pool_state.pool_info.share_price - pool_state.pool_info.long_exposure,
            latest_block_number,
        )
        failed = True

    # Creating a checkpoint should never fail
    # TODO: add get_block_transactions() to interface
    transactions = latest_block.get("transactions", None)
    if transactions is None:
        raise AssertionError("Latest block did not have transactions.")
    # TODO: if not, decode the hexbytes
    if isinstance(transactions, Sequence):
        # If any transaction is to hyperdrive then assert a checkpoint happened
        for transaction in transactions:
            if isinstance(transaction, HexBytes):
                # If hexbytes, there was no trade
                continue
            txn_to = transaction.get("to", None)
            if txn_to is None:
                raise AssertionError("Transaction did not have a 'to' key.")
            if txn_to == interface.hyperdrive_contract.address and pool_state.checkpoint.share_price <= 0:
                logging.critical(
                    (
                        "A transaction was created but no checkpoint was minted.\n"
                        "checkpoint.share_price=%s\n"
                        "transaction=%s\n"
                        "block_number=%s"
                    ),
                    pool_state.checkpoint.share_price,
                    transaction,
                    latest_block_number,
                )
                failed = True

    # Log additional information if any test failed
    if failed:
        logging.info(
            "pool_config = %s\n\npool_info = %s\n\nlatest_checkpoint = %s\n\nadditional_info = %s",
            json.dumps(asdict(pool_state.pool_config), indent=2, cls=ExtendedJSONEncoder),
            json.dumps(asdict(pool_state.pool_info), indent=2, cls=ExtendedJSONEncoder),
            json.dumps(asdict(pool_state.checkpoint), indent=2, cls=ExtendedJSONEncoder),
            json.dumps(
                {
                    "hyperdrive_address": interface.hyperdrive_contract.address,
                    "base_token_address": interface.base_token_contract.address,
                    "spot_price": interface.calc_spot_price(pool_state),
                    "fixed_rate": interface.calc_fixed_rate(pool_state),
                    "variable_rate": pool_state.variable_rate,
                    "vault_shares": pool_state.vault_shares,
                },
                indent=2,
                cls=ExtendedJSONEncoder,
            ),
        )


class Args(NamedTuple):
    """Command line arguments for the invariant checker."""

    eth_config_env_file: str
    test_epsilon: int
    sleep_time: int


def namespace_to_args(namespace: argparse.Namespace) -> Args:
    """Converts argprase.Namespace to Args.

    Arguments
    ---------
    namespace: argparse.Namespace
        Object for storing arg attributes.

    Returns
    -------
    Args
        Formatted arguments
    """
    return Args(
        eth_config_env_file=namespace.eth_config_env_file,
        test_epsilon=namespace.test_epsilon,
        sleep_time=namespace.sleep_time,
    )


def parse_arguments(argv: Sequence[str] | None = None) -> Args:
    """Parses input arguments.

    Arguments
    ---------
    argv: Sequence[str]
        The argv values returned from argparser.

    Returns
    -------
    Args
        Formatted arguments
    """
    parser = argparse.ArgumentParser(description="Runs a loop to check Hyperdrive invariants at each block.")
    parser.add_argument(
        "--test_epsilon",
        type=float,
        default=1e-4,
        help="The allowed error for equality tests.",
    )
    parser.add_argument(
        "--eth_config_env_file",
        type=str,
        default="eth.env",
        help="String pointing to eth config env file.",
    )
    parser.add_argument(
        "--sleep_time",
        type=int,
        default=5,
        help="Sleep time between checks, in seconds.",
    )

    # Use system arguments if none were passed
    if argv is None:
        argv = sys.argv

    return namespace_to_args(parser.parse_args())


if __name__ == "__main__":
    main()
