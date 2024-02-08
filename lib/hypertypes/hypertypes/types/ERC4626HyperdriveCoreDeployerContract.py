"""A web3.py Contract class for the ERC4626HyperdriveCoreDeployer contract.

DO NOT EDIT.  This file was generated by pypechain.  See documentation at
https://github.com/delvtech/pypechain"""

# contracts have PascalCase names
# pylint: disable=invalid-name

# contracts control how many attributes and arguments we have in generated code
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments

# we don't need else statement if the other conditionals all have return,
# but it's easier to generate
# pylint: disable=no-else-return

# This file is bound to get very long depending on contract sizes.
# pylint: disable=too-many-lines

# methods are overriden with specific arguments instead of generic *args, **kwargs
# pylint: disable=arguments-differ

# consumers have too many opinions on line length
# pylint: disable=line-too-long


from __future__ import annotations

from typing import Any, Type, cast

from eth_account.signers.local import LocalAccount
from eth_typing import ChecksumAddress, HexStr
from hexbytes import HexBytes
from typing_extensions import Self
from web3 import Web3
from web3.contract.contract import Contract, ContractConstructor, ContractFunction, ContractFunctions
from web3.exceptions import FallbackNotFound
from web3.types import ABI, BlockIdentifier, CallOverride, TxParams

from .IHyperdriveTypes import Fees, PoolConfig
from .utilities import dataclass_to_tuple, rename_returned_types

structs = {
    "Fees": Fees,
    "PoolConfig": PoolConfig,
}


class ERC4626HyperdriveCoreDeployerDeployContractFunction(ContractFunction):
    """ContractFunction for the deploy method."""

    def __call__(self, config: PoolConfig, extraData: bytes, target0: str, target1: str, target2: str, target3: str, target4: str, salt: bytes) -> ERC4626HyperdriveCoreDeployerDeployContractFunction:  # type: ignore
        clone = super().__call__(
            dataclass_to_tuple(config),
            dataclass_to_tuple(extraData),
            dataclass_to_tuple(target0),
            dataclass_to_tuple(target1),
            dataclass_to_tuple(target2),
            dataclass_to_tuple(target3),
            dataclass_to_tuple(target4),
            dataclass_to_tuple(salt),
        )
        self.kwargs = clone.kwargs
        self.args = clone.args
        return self

    def call(
        self,
        transaction: TxParams | None = None,
        block_identifier: BlockIdentifier = "latest",
        state_override: CallOverride | None = None,
        ccip_read_enabled: bool | None = None,
    ) -> str:
        """returns str."""
        # Define the expected return types from the smart contract call

        return_types = str

        # Call the function

        raw_values = super().call(transaction, block_identifier, state_override, ccip_read_enabled)
        return cast(str, rename_returned_types(structs, return_types, raw_values))


class ERC4626HyperdriveCoreDeployerContractFunctions(ContractFunctions):
    """ContractFunctions for the ERC4626HyperdriveCoreDeployer contract."""

    deploy: ERC4626HyperdriveCoreDeployerDeployContractFunction

    def __init__(
        self,
        abi: ABI,
        w3: "Web3",
        address: ChecksumAddress | None = None,
        decode_tuples: bool | None = False,
    ) -> None:
        super().__init__(abi, w3, address, decode_tuples)
        self.deploy = ERC4626HyperdriveCoreDeployerDeployContractFunction.factory(
            "deploy",
            w3=w3,
            contract_abi=abi,
            address=address,
            decode_tuples=decode_tuples,
            function_identifier="deploy",
        )


erc4626hyperdrivecoredeployer_abi: ABI = cast(
    ABI,
    [
        {
            "type": "function",
            "name": "deploy",
            "inputs": [
                {
                    "name": "_config",
                    "type": "tuple",
                    "internalType": "struct IHyperdrive.PoolConfig",
                    "components": [
                        {"name": "baseToken", "type": "address", "internalType": "contract IERC20"},
                        {"name": "linkerFactory", "type": "address", "internalType": "address"},
                        {"name": "linkerCodeHash", "type": "bytes32", "internalType": "bytes32"},
                        {"name": "initialVaultSharePrice", "type": "uint256", "internalType": "uint256"},
                        {"name": "minimumShareReserves", "type": "uint256", "internalType": "uint256"},
                        {"name": "minimumTransactionAmount", "type": "uint256", "internalType": "uint256"},
                        {"name": "positionDuration", "type": "uint256", "internalType": "uint256"},
                        {"name": "checkpointDuration", "type": "uint256", "internalType": "uint256"},
                        {"name": "timeStretch", "type": "uint256", "internalType": "uint256"},
                        {"name": "governance", "type": "address", "internalType": "address"},
                        {"name": "feeCollector", "type": "address", "internalType": "address"},
                        {
                            "name": "fees",
                            "type": "tuple",
                            "internalType": "struct IHyperdrive.Fees",
                            "components": [
                                {"name": "curve", "type": "uint256", "internalType": "uint256"},
                                {"name": "flat", "type": "uint256", "internalType": "uint256"},
                                {"name": "governanceLP", "type": "uint256", "internalType": "uint256"},
                                {"name": "governanceZombie", "type": "uint256", "internalType": "uint256"},
                            ],
                        },
                    ],
                },
                {"name": "_extraData", "type": "bytes", "internalType": "bytes"},
                {"name": "_target0", "type": "address", "internalType": "address"},
                {"name": "_target1", "type": "address", "internalType": "address"},
                {"name": "_target2", "type": "address", "internalType": "address"},
                {"name": "_target3", "type": "address", "internalType": "address"},
                {"name": "_target4", "type": "address", "internalType": "address"},
                {"name": "_salt", "type": "bytes32", "internalType": "bytes32"},
            ],
            "outputs": [{"name": "", "type": "address", "internalType": "address"}],
            "stateMutability": "nonpayable",
        }
    ],
)
# pylint: disable=line-too-long
erc4626hyperdrivecoredeployer_bytecode = HexStr(
    "0x608060405234801561001057600080fd5b50611fab806100206000396000f3fe60806040523480156200001157600080fd5b50600436106200002e5760003560e01c80630c65a1cb1462000033575b600080fd5b6200004a6200004436600462000256565b62000066565b6040516001600160a01b03909116815260200160405180910390f35b600080888060200190518101906200007f9190620003ce565b9050828a8989898989876040516200009790620000db565b620000a99796959493929190620003f5565b8190604051809103906000f5905080158015620000ca573d6000803e3d6000fd5b509150505b98975050505050505050565b611a3f806200053783390190565b634e487b7160e01b600052604160045260246000fd5b604051610180810167ffffffffffffffff81118282101715620001265762000126620000e9565b60405290565b6001600160a01b03811681146200014257600080fd5b50565b803562000152816200012c565b919050565b6000608082840312156200016a57600080fd5b6040516080810181811067ffffffffffffffff82111715620001905762000190620000e9565b8060405250809150823581526020830135602082015260408301356040820152606083013560608201525092915050565b600082601f830112620001d357600080fd5b813567ffffffffffffffff80821115620001f157620001f1620000e9565b604051601f8301601f19908116603f011681019082821181831017156200021c576200021c620000e9565b816040528381528660208588010111156200023657600080fd5b836020870160208301376000602085830101528094505050505092915050565b600080600080600080600080888a036102c08112156200027557600080fd5b6101e0808212156200028657600080fd5b62000290620000ff565b91506200029d8b62000145565b8252620002ad60208c0162000145565b602083015260408b0135604083015260608b0135606083015260808b0135608083015260a08b013560a083015260c08b013560c083015260e08b013560e0830152610100808c013581840152506101206200030a818d0162000145565b908301526101406200031e8c820162000145565b90830152610160620003338d8d830162000157565b9083015290985089013567ffffffffffffffff8111156200035357600080fd5b620003618b828c01620001c1565b975050620003736102008a0162000145565b9550620003846102208a0162000145565b9450620003956102408a0162000145565b9350620003a66102608a0162000145565b9250620003b76102808a0162000145565b91506102a089013590509295985092959890939650565b600060208284031215620003e157600080fd5b8151620003ee816200012c565b9392505050565b87516001600160a01b031681526102a0810160208901516200042260208401826001600160a01b03169052565b5060408901516040830152606089015160608301526080890151608083015260a089015160a083015260c089015160c083015260e089015160e0830152610100808a01518184015250610120808a015162000487828501826001600160a01b03169052565b5050610140898101516001600160a01b03811684830152505061016089810151805184830152602081015161018085015260408101516101a085015260608101516101c085015250506001600160a01b0388166101e08301526001600160a01b0387166102008301526001600160a01b0386166102208301526001600160a01b0385166102408301526001600160a01b0384166102608301526001600160a01b038316610280830152620000cf56fe6103206040523480156200001257600080fd5b5060405162001a3f38038062001a3f8339810160408190526200003591620006b3565b6001600081905587516001600160a01b0390811660809081526060808b015161018052908a01516101a05260a0808b01516101c05260e0808c015190915260c0808c01519052610100808c0151909152610160808c0180515190925281516020908101516101209081528351604090810151610140908152945190950151909252808d0151851661020052838d015161022052908c0151600880549186166001600160a01b0319909216919091179055908b015183166101e052828a166102405282891661026052828816610280528287166102a0529185166102c05280518082018252928352603160f81b9282019290925290518291899189918991899189918991620001aa917f2aef22f9d7df5f9d21c56d14029233f3fdaa91917727e1eb68e504d27072d6cd917fc89efdaa54c0f20c7adf612882df0950f5a951637e0307cdcb4c672f298b8bc6914691309101938452602084019290925260408301526001600160a01b0316606082015260800190565b60408051601f1981840301815282825280516020918201206102e0526001600160a01b039099166103008190526338d52e0f60e01b8352905190986338d52e0f98506004808401985090965090945090849003019150829050865afa15801562000218573d6000803e3d6000fd5b505050506040513d601f19601f820116820180604052508101906200023e919062000809565b6001600160a01b031687600001516001600160a01b0316146200027457604051630722152560e11b815260040160405180910390fd5b61030051875162000293916001600160a01b03909116906001620002a0565b505050505050506200087e565b604080516001600160a01b038416602482015260448082018490528251808303909101815260649091019091526020810180516001600160e01b0390811663095ea7b360e01b17909152620002fa90859083906200036c16565b6200036657604080516001600160a01b038516602482015260006044808301919091528251808303909101815260649091019091526020810180516001600160e01b0390811663095ea7b360e01b179091526200035a9186916200041d16565b6200036684826200041d565b50505050565b6000806000846001600160a01b0316846040516200038b919062000829565b6000604051808303816000865af19150503d8060008114620003ca576040519150601f19603f3d011682016040523d82523d6000602084013e620003cf565b606091505b5091509150818015620003fd575080511580620003fd575080806020019051810190620003fd91906200085a565b80156200041457506000856001600160a01b03163b115b95945050505050565b6000620004346001600160a01b0384168362000490565b905080516000141580156200045c5750808060200190518101906200045a91906200085a565b155b156200048b57604051635274afe760e01b81526001600160a01b03841660048201526024015b60405180910390fd5b505050565b6060620004a083836000620004a7565b9392505050565b606081471015620004ce5760405163cd78605960e01b815230600482015260240162000482565b600080856001600160a01b03168486604051620004ec919062000829565b60006040518083038185875af1925050503d80600081146200052b576040519150601f19603f3d011682016040523d82523d6000602084013e62000530565b606091505b509092509050620005438683836200054d565b9695505050505050565b60608262000566576200056082620005b1565b620004a0565b81511580156200057e57506001600160a01b0384163b155b15620005a957604051639996b31560e01b81526001600160a01b038516600482015260240162000482565b5080620004a0565b805115620005c25780518082602001fd5b604051630a12f52160e11b815260040160405180910390fd5b50565b60405161018081016001600160401b03811182821017156200061057634e487b7160e01b600052604160045260246000fd5b60405290565b6001600160a01b0381168114620005db57600080fd5b8051620006398162000616565b919050565b6000608082840312156200065157600080fd5b604051608081016001600160401b03811182821017156200068257634e487b7160e01b600052604160045260246000fd5b8060405250809150825181526020830151602082015260408301516040820152606083015160608201525092915050565b60008060008060008060008789036102a0811215620006d157600080fd5b6101e080821215620006e257600080fd5b620006ec620005de565b9150620006f98a6200062c565b82526200070960208b016200062c565b602083015260408a0151604083015260608a0151606083015260808a0151608083015260a08a015160a083015260c08a015160c083015260e08a015160e0830152610100808b0151818401525061012062000766818c016200062c565b908301526101406200077a8b82016200062c565b908301526101606200078f8c8c83016200063e565b8184015250819850620007a4818b016200062c565b97505050620007b761020089016200062c565b9450620007c861022089016200062c565b9350620007d961024089016200062c565b9250620007ea61026089016200062c565b9150620007fb61028089016200062c565b905092959891949750929550565b6000602082840312156200081c57600080fd5b8151620004a08162000616565b6000825160005b818110156200084c576020818601810151858301520162000830565b506000920191825250919050565b6000602082840312156200086d57600080fd5b81518015158114620004a057600080fd5b60805160a05160c05160e05161010051610120516101405161016051610180516101a0516101c0516101e05161020051610220516102405161026051610280516102a0516102c0516102e05161030051611082620009bd600039600050506000818161043e015261081b01526000818161063501526109cd01526000818161057a0152610997015260008181610533015281816107220152610a270152600081816105e10152818161068c0152818161078701526107ea0152600081816101ce015281816103900152818161065c015281816106be015281816106f001528181610756015281816107ba015281816108ac0152818161096501526109f6015260005050600050506000505060005050600050506000505060005050600050506000505060005050600050506000505060005050600050506110826000f3fe6080604052600436106101b75760003560e01c80639032c726116100ec578063d899e1121161008a578063e44808bc11610064578063e44808bc146105af578063eac3e799146105cf578063ed64bab214610603578063f3f7070714610623576101b7565b8063d899e11214610568578063dbbe80701461059c578063ded06231146103ca576101b7565b8063a6e8a859116100c6578063a6e8a85914610521578063ab033ea9146102c7578063cba2e58d14610555578063cbc1343414610304576101b7565b80639032c726146104e15780639cd241af14610501578063a22cb465146104ae576101b7565b806330adf81f116101595780634c2ac1d9116101335780634c2ac1d9146104805780634ed2d6ac146104935780637180c8ca146104ae57806377d05ff4146104ce576101b7565b806330adf81f146103f85780633644e5151461042c5780633e691db914610460576101b7565b806317fad7fc1161019557806317fad7fc1461033e5780631c0f12b61461035e57806321b57d531461037e57806329b23fc1146103ca576101b7565b806301681a62146102c757806302329a29146102e9578063074a6de914610304575b3480156101c357600080fd5b5060003660606000807f00000000000000000000000000000000000000000000000000000000000000006001600160a01b03168585604051610206929190610a63565b600060405180830381855af49150503d8060008114610241576040519150601f19603f3d011682016040523d82523d6000602084013e610246565b606091505b5091509150811561026a57604051638bb0a34b60e01b815260040160405180910390fd5b600061027582610a73565b90506001600160e01b03198116636e64089360e11b1461029757815160208301fd5b8151600319810160048401908152926102b891810160200190602401610ae4565b80519650602001945050505050f35b3480156102d357600080fd5b506102e76102e2366004610ba9565b610657565b005b3480156102f557600080fd5b506102e76102e2366004610be2565b34801561031057600080fd5b5061032461031f366004610c0f565b610684565b604080519283526020830191909152015b60405180910390f35b34801561034a57600080fd5b506102e7610359366004610cab565b6106b9565b34801561036a57600080fd5b506102e7610379366004610d40565b6106eb565b34801561038a57600080fd5b506103b27f000000000000000000000000000000000000000000000000000000000000000081565b6040516001600160a01b039091168152602001610335565b3480156103d657600080fd5b506103ea6103e5366004610d88565b61071b565b604051908152602001610335565b34801561040457600080fd5b506103ea7f65619c8664d6db8aae8c236ad19598696159942a4245b23b45565cc18e97367381565b34801561043857600080fd5b506103ea7f000000000000000000000000000000000000000000000000000000000000000081565b34801561046c57600080fd5b506103ea61047b366004610de2565b61074f565b6103ea61048e366004610e1f565b610780565b34801561049f57600080fd5b506102e7610379366004610e83565b3480156104ba57600080fd5b506102e76104c9366004610ecd565b6107b5565b6103ea6104dc366004610c0f565b6107e3565b3480156104ed57600080fd5b506102e76104fc366004610f02565b610816565b34801561050d57600080fd5b506102e761051c366004610f80565b610960565b34801561052d57600080fd5b506103b27f000000000000000000000000000000000000000000000000000000000000000081565b610324610563366004610d88565b61098f565b34801561057457600080fd5b506103b27f000000000000000000000000000000000000000000000000000000000000000081565b6103246105aa366004610d88565b6109c5565b3480156105bb57600080fd5b506102e76105ca366004610fb8565b6109f1565b3480156105db57600080fd5b506103b27f000000000000000000000000000000000000000000000000000000000000000081565b34801561060f57600080fd5b506102e761061e366004611017565b610a22565b34801561062f57600080fd5b506103b27f000000000000000000000000000000000000000000000000000000000000000081565b6106807f0000000000000000000000000000000000000000000000000000000000000000610a47565b5050565b6000806106b07f0000000000000000000000000000000000000000000000000000000000000000610a47565b50935093915050565b6106e27f0000000000000000000000000000000000000000000000000000000000000000610a47565b50505050505050565b6107147f0000000000000000000000000000000000000000000000000000000000000000610a47565b5050505050565b60006107467f0000000000000000000000000000000000000000000000000000000000000000610a47565b50949350505050565b600061077a7f0000000000000000000000000000000000000000000000000000000000000000610a47565b50919050565b60006107ab7f0000000000000000000000000000000000000000000000000000000000000000610a47565b5095945050505050565b6107de7f0000000000000000000000000000000000000000000000000000000000000000610a47565b505050565b600061080e7f0000000000000000000000000000000000000000000000000000000000000000610a47565b509392505050565b6040517f000000000000000000000000000000000000000000000000000000000000000060248201527f65619c8664d6db8aae8c236ad19598696159942a4245b23b45565cc18e97367360448201526001600160a01b038881166064830152878116608483015286151560a483015260c4820186905260ff851660e48301526101048201849052610124820183905260009182917f000000000000000000000000000000000000000000000000000000000000000016906101440160408051601f198184030181529181526020820180516001600160e01b03166314e5f07b60e01b179052516109069190611030565b600060405180830381855af49150503d8060008114610941576040519150601f19603f3d011682016040523d82523d6000602084013e610946565b606091505b50915091508161095857805160208201fd5b805160208201f35b6109897f0000000000000000000000000000000000000000000000000000000000000000610a47565b50505050565b6000806109bb7f0000000000000000000000000000000000000000000000000000000000000000610a47565b5094509492505050565b6000806109bb7f0000000000000000000000000000000000000000000000000000000000000000610a47565b610a1a7f0000000000000000000000000000000000000000000000000000000000000000610a47565b505050505050565b6106807f00000000000000000000000000000000000000000000000000000000000000005b6060600080836001600160a01b03166000366040516109069291905b8183823760009101908152919050565b805160208201516001600160e01b03198082169291906004831015610aa25780818460040360031b1b83161693505b505050919050565b634e487b7160e01b600052604160045260246000fd5b60005b83811015610adb578181015183820152602001610ac3565b50506000910152565b600060208284031215610af657600080fd5b815167ffffffffffffffff80821115610b0e57600080fd5b818401915084601f830112610b2257600080fd5b815181811115610b3457610b34610aaa565b604051601f8201601f19908116603f01168101908382118183101715610b5c57610b5c610aaa565b81604052828152876020848701011115610b7557600080fd5b610b86836020830160208801610ac0565b979650505050505050565b6001600160a01b0381168114610ba657600080fd5b50565b600060208284031215610bbb57600080fd5b8135610bc681610b91565b9392505050565b80358015158114610bdd57600080fd5b919050565b600060208284031215610bf457600080fd5b610bc682610bcd565b60006060828403121561077a57600080fd5b600080600060608486031215610c2457600080fd5b8335925060208401359150604084013567ffffffffffffffff811115610c4957600080fd5b610c5586828701610bfd565b9150509250925092565b60008083601f840112610c7157600080fd5b50813567ffffffffffffffff811115610c8957600080fd5b6020830191508360208260051b8501011115610ca457600080fd5b9250929050565b60008060008060008060808789031215610cc457600080fd5b8635610ccf81610b91565b95506020870135610cdf81610b91565b9450604087013567ffffffffffffffff80821115610cfc57600080fd5b610d088a838b01610c5f565b90965094506060890135915080821115610d2157600080fd5b50610d2e89828a01610c5f565b979a9699509497509295939492505050565b60008060008060808587031215610d5657600080fd5b843593506020850135610d6881610b91565b92506040850135610d7881610b91565b9396929550929360600135925050565b60008060008060808587031215610d9e57600080fd5b843593506020850135925060408501359150606085013567ffffffffffffffff811115610dca57600080fd5b610dd687828801610bfd565b91505092959194509250565b600060208284031215610df457600080fd5b813567ffffffffffffffff811115610e0b57600080fd5b610e1784828501610bfd565b949350505050565b600080600080600060a08688031215610e3757600080fd5b85359450602086013593506040860135925060608601359150608086013567ffffffffffffffff811115610e6a57600080fd5b610e7688828901610bfd565b9150509295509295909350565b60008060008060808587031215610e9957600080fd5b843593506020850135610eab81610b91565b9250604085013591506060850135610ec281610b91565b939692955090935050565b60008060408385031215610ee057600080fd5b8235610eeb81610b91565b9150610ef960208401610bcd565b90509250929050565b600080600080600080600060e0888a031215610f1d57600080fd5b8735610f2881610b91565b96506020880135610f3881610b91565b9550610f4660408901610bcd565b945060608801359350608088013560ff81168114610f6357600080fd5b9699959850939692959460a0840135945060c09093013592915050565b600080600060608486031215610f9557600080fd5b833592506020840135610fa781610b91565b929592945050506040919091013590565b600080600080600060a08688031215610fd057600080fd5b853594506020860135610fe281610b91565b93506040860135610ff281610b91565b925060608601359150608086013561100981610b91565b809150509295509295909350565b60006020828403121561102957600080fd5b5035919050565b60008251611042818460208701610ac0565b919091019291505056fea26469706673582212206ac9ce75bf4ddf305384946e82b4437bb7fb85984cc1fa2652b9e7ac12720ede64736f6c63430008140033a26469706673582212203bc34388df3c7b1535f5d7f640ae92139d6d62aa8954dd70f1e7d37a78006fa364736f6c63430008140033"
)


class ERC4626HyperdriveCoreDeployerContract(Contract):
    """A web3.py Contract class for the ERC4626HyperdriveCoreDeployer contract."""

    abi: ABI = erc4626hyperdrivecoredeployer_abi
    bytecode: bytes = HexBytes(erc4626hyperdrivecoredeployer_bytecode)

    def __init__(self, address: ChecksumAddress | None = None) -> None:
        try:
            # Initialize parent Contract class
            super().__init__(address=address)
            self.functions = ERC4626HyperdriveCoreDeployerContractFunctions(erc4626hyperdrivecoredeployer_abi, self.w3, address)  # type: ignore

        except FallbackNotFound:
            print("Fallback function not found. Continuing...")

    functions: ERC4626HyperdriveCoreDeployerContractFunctions

    @classmethod
    def constructor(cls) -> ContractConstructor:  # type: ignore
        """Creates a transaction with the contract's constructor function.

        Parameters
        ----------

        w3 : Web3
            A web3 instance.
        account : LocalAccount
            The account to use to deploy the contract.

        Returns
        -------
        Self
            A deployed instance of the contract.

        """

        return super().constructor()

    @classmethod
    def deploy(cls, w3: Web3, account: LocalAccount | ChecksumAddress) -> Self:
        """Deploys and instance of the contract.

        Parameters
        ----------
        w3 : Web3
            A web3 instance.
        account : LocalAccount
            The account to use to deploy the contract.

        Returns
        -------
        Self
            A deployed instance of the contract.
        """
        deployer = cls.factory(w3=w3)
        constructor_fn = deployer.constructor()

        # if an address is supplied, try to use a web3 default account
        if isinstance(account, str):
            tx_hash = constructor_fn.transact({"from": account})
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            deployed_contract = deployer(address=tx_receipt.contractAddress)  # type: ignore
            return deployed_contract

        # otherwise use the account provided.
        deployment_tx = constructor_fn.build_transaction()
        current_nonce = w3.eth.get_transaction_count(account.address)
        deployment_tx.update({"nonce": current_nonce})

        # Sign the transaction with local account private key
        signed_tx = account.sign_transaction(deployment_tx)

        # Send the signed transaction and wait for receipt
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        deployed_contract = deployer(address=tx_receipt.contractAddress)  # type: ignore
        return deployed_contract

    @classmethod
    def factory(cls, w3: Web3, class_name: str | None = None, **kwargs: Any) -> Type[Self]:
        """Deploys and instance of the contract.

        Parameters
        ----------
        w3 : Web3
            A web3 instance.
        class_name: str | None
            The instance class name.

        Returns
        -------
        Self
            A deployed instance of the contract.
        """
        contract = super().factory(w3, class_name, **kwargs)
        contract.functions = ERC4626HyperdriveCoreDeployerContractFunctions(erc4626hyperdrivecoredeployer_abi, w3, None)

        return contract
