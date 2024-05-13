"""Dataclasses for all structs in the IHyperdrive contract.

DO NOT EDIT.  This file was generated by pypechain.  See documentation at
https://github.com/delvtech/pypechain """

# super() call methods are generic, while our version adds values & types
# pylint: disable=arguments-differ

# contracts have PascalCase names
# pylint: disable=invalid-name
# contracts control how many attributes and arguments we have in generated code
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# unable to determine which imports will be used in the generated code
# pylint: disable=unused-import
# we don't need else statement if the other conditionals all have return,
# but it's easier to generate
# pylint: disable=no-else-return
from __future__ import annotations

from dataclasses import dataclass

from web3.types import ABIEvent, ABIEventParams


@dataclass
class Options:
    """Options struct."""

    destination: str
    asBase: bool
    extraData: bytes


@dataclass
class Checkpoint:
    """Checkpoint struct."""

    weightedSpotPrice: int
    lastWeightedSpotPriceUpdateTime: int
    vaultSharePrice: int


@dataclass
class MarketState:
    """MarketState struct."""

    shareReserves: int
    bondReserves: int
    longExposure: int
    longsOutstanding: int
    shareAdjustment: int
    shortsOutstanding: int
    longAverageMaturityTime: int
    shortAverageMaturityTime: int
    isInitialized: bool
    isPaused: bool
    zombieBaseProceeds: int
    zombieShareReserves: int


@dataclass
class Fees:
    """Fees struct."""

    curve: int
    flat: int
    governanceLP: int
    governanceZombie: int


@dataclass
class PoolConfig:
    """PoolConfig struct."""

    baseToken: str
    vaultSharesToken: str
    linkerFactory: str
    linkerCodeHash: bytes
    initialVaultSharePrice: int
    minimumShareReserves: int
    minimumTransactionAmount: int
    circuitBreakerDelta: int
    positionDuration: int
    checkpointDuration: int
    timeStretch: int
    governance: str
    feeCollector: str
    sweepCollector: str
    fees: Fees


@dataclass
class PoolInfo:
    """PoolInfo struct."""

    shareReserves: int
    shareAdjustment: int
    zombieBaseProceeds: int
    zombieShareReserves: int
    bondReserves: int
    lpTotalSupply: int
    vaultSharePrice: int
    longsOutstanding: int
    longAverageMaturityTime: int
    shortsOutstanding: int
    shortAverageMaturityTime: int
    withdrawalSharesReadyToWithdraw: int
    withdrawalSharesProceeds: int
    lpSharePrice: int
    longExposure: int


@dataclass
class WithdrawPool:
    """WithdrawPool struct."""

    readyToWithdraw: int
    proceeds: int


@dataclass
class PoolDeployConfig:
    """PoolDeployConfig struct."""

    baseToken: str
    vaultSharesToken: str
    linkerFactory: str
    linkerCodeHash: bytes
    minimumShareReserves: int
    minimumTransactionAmount: int
    circuitBreakerDelta: int
    positionDuration: int
    checkpointDuration: int
    timeStretch: int
    governance: str
    feeCollector: str
    sweepCollector: str
    fees: Fees


AddLiquidity = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="provider", type="address"),
        ABIEventParams(indexed=False, name="lpAmount", type="uint256"),
        ABIEventParams(indexed=False, name="baseAmount", type="uint256"),
        ABIEventParams(indexed=False, name="vaultShareAmount", type="uint256"),
        ABIEventParams(indexed=False, name="asBase", type="bool"),
        ABIEventParams(indexed=False, name="lpSharePrice", type="uint256"),
    ],
    name="AddLiquidity",
    type="event",
)

Approval = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="owner", type="address"),
        ABIEventParams(indexed=True, name="spender", type="address"),
        ABIEventParams(indexed=False, name="value", type="uint256"),
    ],
    name="Approval",
    type="event",
)

ApprovalForAll = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="account", type="address"),
        ABIEventParams(indexed=True, name="operator", type="address"),
        ABIEventParams(indexed=False, name="approved", type="bool"),
    ],
    name="ApprovalForAll",
    type="event",
)

CloseLong = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="trader", type="address"),
        ABIEventParams(indexed=True, name="destination", type="address"),
        ABIEventParams(indexed=True, name="assetId", type="uint256"),
        ABIEventParams(indexed=False, name="maturityTime", type="uint256"),
        ABIEventParams(indexed=False, name="baseAmount", type="uint256"),
        ABIEventParams(indexed=False, name="vaultShareAmount", type="uint256"),
        ABIEventParams(indexed=False, name="asBase", type="bool"),
        ABIEventParams(indexed=False, name="bondAmount", type="uint256"),
    ],
    name="CloseLong",
    type="event",
)

CloseShort = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="trader", type="address"),
        ABIEventParams(indexed=True, name="destination", type="address"),
        ABIEventParams(indexed=True, name="assetId", type="uint256"),
        ABIEventParams(indexed=False, name="maturityTime", type="uint256"),
        ABIEventParams(indexed=False, name="baseAmount", type="uint256"),
        ABIEventParams(indexed=False, name="vaultShareAmount", type="uint256"),
        ABIEventParams(indexed=False, name="asBase", type="bool"),
        ABIEventParams(indexed=False, name="basePayment", type="uint256"),
        ABIEventParams(indexed=False, name="bondAmount", type="uint256"),
    ],
    name="CloseShort",
    type="event",
)

CollectGovernanceFee = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="collector", type="address"),
        ABIEventParams(indexed=False, name="fees", type="uint256"),
    ],
    name="CollectGovernanceFee",
    type="event",
)

CreateCheckpoint = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="checkpointTime", type="uint256"),
        ABIEventParams(indexed=False, name="checkpointVaultSharePrice", type="uint256"),
        ABIEventParams(indexed=False, name="vaultSharePrice", type="uint256"),
        ABIEventParams(indexed=False, name="maturedShorts", type="uint256"),
        ABIEventParams(indexed=False, name="maturedLongs", type="uint256"),
        ABIEventParams(indexed=False, name="lpSharePrice", type="uint256"),
    ],
    name="CreateCheckpoint",
    type="event",
)

FeeCollectorUpdated = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="newFeeCollector", type="address"),
    ],
    name="FeeCollectorUpdated",
    type="event",
)

GovernanceUpdated = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="newGovernance", type="address"),
    ],
    name="GovernanceUpdated",
    type="event",
)

Initialize = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="provider", type="address"),
        ABIEventParams(indexed=False, name="lpAmount", type="uint256"),
        ABIEventParams(indexed=False, name="baseAmount", type="uint256"),
        ABIEventParams(indexed=False, name="vaultShareAmount", type="uint256"),
        ABIEventParams(indexed=False, name="asBase", type="bool"),
        ABIEventParams(indexed=False, name="apr", type="uint256"),
    ],
    name="Initialize",
    type="event",
)

OpenLong = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="trader", type="address"),
        ABIEventParams(indexed=True, name="assetId", type="uint256"),
        ABIEventParams(indexed=False, name="maturityTime", type="uint256"),
        ABIEventParams(indexed=False, name="baseAmount", type="uint256"),
        ABIEventParams(indexed=False, name="vaultShareAmount", type="uint256"),
        ABIEventParams(indexed=False, name="asBase", type="bool"),
        ABIEventParams(indexed=False, name="bondAmount", type="uint256"),
    ],
    name="OpenLong",
    type="event",
)

OpenShort = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="trader", type="address"),
        ABIEventParams(indexed=True, name="assetId", type="uint256"),
        ABIEventParams(indexed=False, name="maturityTime", type="uint256"),
        ABIEventParams(indexed=False, name="baseAmount", type="uint256"),
        ABIEventParams(indexed=False, name="vaultShareAmount", type="uint256"),
        ABIEventParams(indexed=False, name="asBase", type="bool"),
        ABIEventParams(indexed=False, name="baseProceeds", type="uint256"),
        ABIEventParams(indexed=False, name="bondAmount", type="uint256"),
    ],
    name="OpenShort",
    type="event",
)

PauseStatusUpdated = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=False, name="isPaused", type="bool"),
    ],
    name="PauseStatusUpdated",
    type="event",
)

PauserUpdated = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="newPauser", type="address"),
        ABIEventParams(indexed=False, name="status", type="bool"),
    ],
    name="PauserUpdated",
    type="event",
)

RedeemWithdrawalShares = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="provider", type="address"),
        ABIEventParams(indexed=True, name="destination", type="address"),
        ABIEventParams(indexed=False, name="withdrawalShareAmount", type="uint256"),
        ABIEventParams(indexed=False, name="baseAmount", type="uint256"),
        ABIEventParams(indexed=False, name="vaultShareAmount", type="uint256"),
        ABIEventParams(indexed=False, name="asBase", type="bool"),
    ],
    name="RedeemWithdrawalShares",
    type="event",
)

RemoveLiquidity = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="provider", type="address"),
        ABIEventParams(indexed=True, name="destination", type="address"),
        ABIEventParams(indexed=False, name="lpAmount", type="uint256"),
        ABIEventParams(indexed=False, name="baseAmount", type="uint256"),
        ABIEventParams(indexed=False, name="vaultShareAmount", type="uint256"),
        ABIEventParams(indexed=False, name="asBase", type="bool"),
        ABIEventParams(indexed=False, name="withdrawalShareAmount", type="uint256"),
        ABIEventParams(indexed=False, name="lpSharePrice", type="uint256"),
    ],
    name="RemoveLiquidity",
    type="event",
)

Sweep = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="collector", type="address"),
        ABIEventParams(indexed=True, name="target", type="address"),
    ],
    name="Sweep",
    type="event",
)

SweepCollectorUpdated = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="newSweepCollector", type="address"),
    ],
    name="SweepCollectorUpdated",
    type="event",
)

TransferSingle = ABIEvent(
    anonymous=False,
    inputs=[
        ABIEventParams(indexed=True, name="operator", type="address"),
        ABIEventParams(indexed=True, name="from", type="address"),
        ABIEventParams(indexed=True, name="to", type="address"),
        ABIEventParams(indexed=False, name="id", type="uint256"),
        ABIEventParams(indexed=False, name="value", type="uint256"),
    ],
    name="TransferSingle",
    type="event",
)


@dataclass
class ErrorInfo:
    """Custom contract error information."""

    name: str
    selector: str
    signature: str
    inputs: list[ErrorParams]


@dataclass
class ErrorParams:
    """Parameter info for custom contract errors."""

    name: str
    solidity_type: str
    python_type: str


BatchInputLengthMismatchError = ErrorInfo(
    inputs=[],
    name="BatchInputLengthMismatch",
    selector="0xba430d38",
    signature="BatchInputLengthMismatch()",
)

BelowMinimumContributionError = ErrorInfo(
    inputs=[],
    name="BelowMinimumContribution",
    selector="0xabed41c4",
    signature="BelowMinimumContribution()",
)

CircuitBreakerTriggeredError = ErrorInfo(
    inputs=[],
    name="CircuitBreakerTriggered",
    selector="0x2a958098",
    signature="CircuitBreakerTriggered()",
)

DecreasedPresentValueWhenAddingLiquidityError = ErrorInfo(
    inputs=[],
    name="DecreasedPresentValueWhenAddingLiquidity",
    selector="0x309b2a42",
    signature="DecreasedPresentValueWhenAddingLiquidity()",
)

DistributeExcessIdleFailedError = ErrorInfo(
    inputs=[],
    name="DistributeExcessIdleFailed",
    selector="0x8bdf918d",
    signature="DistributeExcessIdleFailed()",
)

ExpInvalidExponentError = ErrorInfo(
    inputs=[],
    name="ExpInvalidExponent",
    selector="0x73a2d6b1",
    signature="ExpInvalidExponent()",
)

ExpiredDeadlineError = ErrorInfo(
    inputs=[],
    name="ExpiredDeadline",
    selector="0xf87d9271",
    signature="ExpiredDeadline()",
)

InsufficientBalanceError = ErrorInfo(
    inputs=[],
    name="InsufficientBalance",
    selector="0xf4d678b8",
    signature="InsufficientBalance()",
)

InsufficientLiquidityError = ErrorInfo(
    inputs=[],
    name="InsufficientLiquidity",
    selector="0xbb55fd27",
    signature="InsufficientLiquidity()",
)

InvalidAprError = ErrorInfo(
    inputs=[],
    name="InvalidApr",
    selector="0x76c22a22",
    signature="InvalidApr()",
)

InvalidCheckpointTimeError = ErrorInfo(
    inputs=[],
    name="InvalidCheckpointTime",
    selector="0xecd29e81",
    signature="InvalidCheckpointTime()",
)

InvalidERC20BridgeError = ErrorInfo(
    inputs=[],
    name="InvalidERC20Bridge",
    selector="0x2aab8bd3",
    signature="InvalidERC20Bridge()",
)

InvalidEffectiveShareReservesError = ErrorInfo(
    inputs=[],
    name="InvalidEffectiveShareReserves",
    selector="0x85bd2ac4",
    signature="InvalidEffectiveShareReserves()",
)

InvalidFeeDestinationError = ErrorInfo(
    inputs=[],
    name="InvalidFeeDestination",
    selector="0x2b44eccc",
    signature="InvalidFeeDestination()",
)

InvalidInitialVaultSharePriceError = ErrorInfo(
    inputs=[],
    name="InvalidInitialVaultSharePrice",
    selector="0x094b19ad",
    signature="InvalidInitialVaultSharePrice()",
)

InvalidLPSharePriceError = ErrorInfo(
    inputs=[],
    name="InvalidLPSharePrice",
    selector="0xabeba7ee",
    signature="InvalidLPSharePrice()",
)

InvalidPresentValueError = ErrorInfo(
    inputs=[],
    name="InvalidPresentValue",
    selector="0xaa2c6516",
    signature="InvalidPresentValue()",
)

InvalidSignatureError = ErrorInfo(
    inputs=[],
    name="InvalidSignature",
    selector="0x8baa579f",
    signature="InvalidSignature()",
)

InvalidTimestampError = ErrorInfo(
    inputs=[],
    name="InvalidTimestamp",
    selector="0xb7d09497",
    signature="InvalidTimestamp()",
)

LnInvalidInputError = ErrorInfo(
    inputs=[],
    name="LnInvalidInput",
    selector="0xe61b4975",
    signature="LnInvalidInput()",
)

MinimumSharePriceError = ErrorInfo(
    inputs=[],
    name="MinimumSharePrice",
    selector="0x42af972b",
    signature="MinimumSharePrice()",
)

MinimumTransactionAmountError = ErrorInfo(
    inputs=[],
    name="MinimumTransactionAmount",
    selector="0x423bbb46",
    signature="MinimumTransactionAmount()",
)

NotPayableError = ErrorInfo(
    inputs=[],
    name="NotPayable",
    selector="0x1574f9f3",
    signature="NotPayable()",
)

OutputLimitError = ErrorInfo(
    inputs=[],
    name="OutputLimit",
    selector="0xc9726517",
    signature="OutputLimit()",
)

PoolAlreadyInitializedError = ErrorInfo(
    inputs=[],
    name="PoolAlreadyInitialized",
    selector="0x7983c051",
    signature="PoolAlreadyInitialized()",
)

PoolIsPausedError = ErrorInfo(
    inputs=[],
    name="PoolIsPaused",
    selector="0x21081abf",
    signature="PoolIsPaused()",
)

RestrictedZeroAddressError = ErrorInfo(
    inputs=[],
    name="RestrictedZeroAddress",
    selector="0xf0dd15fd",
    signature="RestrictedZeroAddress()",
)

ReturnDataError = ErrorInfo(
    inputs=[
        ErrorParams(name="data", python_type="bytes", solidity_type="bytes"),
    ],
    name="ReturnData",
    selector="0xdcc81126",
    signature="ReturnData(bytes)",
)

SweepFailedError = ErrorInfo(
    inputs=[],
    name="SweepFailed",
    selector="0x9eec2ff8",
    signature="SweepFailed()",
)

TransferFailedError = ErrorInfo(
    inputs=[],
    name="TransferFailed",
    selector="0x90b8ec18",
    signature="TransferFailed()",
)

UnauthorizedError = ErrorInfo(
    inputs=[],
    name="Unauthorized",
    selector="0x82b42900",
    signature="Unauthorized()",
)

UnexpectedSuccessError = ErrorInfo(
    inputs=[],
    name="UnexpectedSuccess",
    selector="0x8bb0a34b",
    signature="UnexpectedSuccess()",
)

UnsafeCastToInt128Error = ErrorInfo(
    inputs=[],
    name="UnsafeCastToInt128",
    selector="0xa5353be5",
    signature="UnsafeCastToInt128()",
)

UnsafeCastToInt256Error = ErrorInfo(
    inputs=[],
    name="UnsafeCastToInt256",
    selector="0x72dd4e02",
    signature="UnsafeCastToInt256()",
)

UnsafeCastToUint112Error = ErrorInfo(
    inputs=[],
    name="UnsafeCastToUint112",
    selector="0x10d62a2e",
    signature="UnsafeCastToUint112()",
)

UnsafeCastToUint128Error = ErrorInfo(
    inputs=[],
    name="UnsafeCastToUint128",
    selector="0x1e15f2a2",
    signature="UnsafeCastToUint128()",
)

UnsupportedTokenError = ErrorInfo(
    inputs=[],
    name="UnsupportedToken",
    selector="0x6a172882",
    signature="UnsupportedToken()",
)

UpdateLiquidityFailedError = ErrorInfo(
    inputs=[],
    name="UpdateLiquidityFailed",
    selector="0x5044b7f5",
    signature="UpdateLiquidityFailed()",
)
