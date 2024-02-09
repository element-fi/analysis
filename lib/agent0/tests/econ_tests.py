"""Tests of economic intuition."""

import pytest

from fixedpointmath import FixedPoint

from agent0.hyperdrive.interactive import InteractiveHyperdrive
from agent0.hyperdrive.interactive.chain import Chain

YEAR_IN_SECONDS = 31_536_000


@pytest.mark.anvil
def test_asymmetry(chain: Chain):
    """Does in equal out?"""
    interactive_config = InteractiveHyperdrive.Config(
        position_duration=YEAR_IN_SECONDS,  # 1 year term
        governance_lp_fee=FixedPoint(0.1),
        curve_fee=FixedPoint(0.01),
        flat_fee=FixedPoint(0),
    )
    interactive_hyperdrive = InteractiveHyperdrive(chain, interactive_config)
    interface = interactive_hyperdrive.interface
    x = interface.calc_shares_out_given_bonds_in_down(FixedPoint(100_000))
    y = interface.calc_shares_in_given_bonds_out_down(FixedPoint(100_000))
    print(x)
    print(y)
    assert x != y
