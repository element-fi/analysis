"""Fixtures for contracts"""
import pytest
from ape.api.accounts import TestAccountAPI
from ape.contracts import ContractInstance
from ape.managers.project import ProjectManager

from .hyperdrive_config import HyperdriveConfig

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="function")
def hyperdrive_data_contract(project: ProjectManager, hyperdrive_contract: ContractInstance) -> ContractInstance:
    """Gets the data provider interface for the hyperdrive contract"""
    print("")
    hyperdrive_data_contract: ContractInstance = project.MockHyperdriveDataProviderTestnet.at(
        hyperdrive_contract.address
    )  # type: ignore
    return hyperdrive_data_contract


@pytest.fixture(scope="function")
def hyperdrive_contract(
    project: ProjectManager, hyperdrive_config: HyperdriveConfig, deployer: TestAccountAPI, base_erc20: ContractInstance
) -> ContractInstance:
    """Deploys the base erc20 contract"""
    hc = hyperdrive_config  # pylint: disable=invalid-name
    # print(f"{project.MockHyperdriveDataProviderTestnet=}")
    # print(f"{base_erc20=}")
    # print(f"{hc.initial_apr=}")
    # print(f"{hc.share_price=}")
    # print(f"{hc.position_duration_seconds=}")
    # print(f"{hc.checkpoint_duration_seconds=}")
    # print(f"{hc.time_stretch=}")
    # print(f"{hc.gov_fee=}")
    # print(f"{hc.flat_fee=}")
    # print(f"{hc.curve_fee=}")
    hyperdrive_data_provider_contract = deployer.deploy(
        project.MockHyperdriveDataProviderTestnet,  # type: ignore
        base_erc20,
        hc.initial_apr,
        hc.share_price,
        hc.position_duration_seconds,
        hc.checkpoint_duration_seconds,
        hc.time_stretch,
        (hc.curve_fee, hc.flat_fee, hc.gov_fee),
        deployer,
    )
    hyperdrive_contract = deployer.deploy(
        project.MockHyperdriveTestnet,  # type: ignore
        hyperdrive_data_provider_contract,
        base_erc20,
        hc.initial_apr,
        hc.share_price,
        hc.position_duration_seconds,
        hc.checkpoint_duration_seconds,
        hc.time_stretch,
        (hc.curve_fee, hc.flat_fee, hc.gov_fee),
        deployer,
    )
    return hyperdrive_contract


class Contracts:
    "Contracts Type"

    def __init__(
        self,
        base_erc20: ContractInstance,
        hyperdrive_contract: ContractInstance,
        hyperdrive_data_contract: ContractInstance,
        fixed_math_contract: ContractInstance,
    ):
        self.base_erc20 = base_erc20
        self.hyperdrive_contract = hyperdrive_contract
        self.hyperdrive_data_contract = hyperdrive_data_contract
        self.fixed_math_contract = fixed_math_contract


@pytest.fixture(scope="function")
def contracts(
    base_erc20: ContractInstance,
    hyperdrive_contract: ContractInstance,
    hyperdrive_data_contract: ContractInstance,
    fixed_math_contract: ContractInstance,
):
    """Returns a Contracts object."""
    return Contracts(
        base_erc20=base_erc20,
        hyperdrive_contract=hyperdrive_contract,
        hyperdrive_data_contract=hyperdrive_data_contract,
        fixed_math_contract=fixed_math_contract,
    )
