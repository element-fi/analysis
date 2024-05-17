"""Example script for using interactive hyperdrive to connect to a remote chain.
"""

# %%
# Variables by themselves print out dataframes in a nice format in interactive mode
# pylint: disable=pointless-statement
# We expect this to be a script, hence no need for uppercase naming
# pylint: disable=invalid-name

from fixedpointmath import FixedPoint

from agent0 import Chain, Hyperdrive, LocalChain, LocalHyperdrive, PolicyZoo
from agent0.core.base.make_key import make_private_key

# %%
# Set the rpc_uri to the chain, e.g., to sepolia testnet
# rpc_uri = "http://uri.to.sepolia.testnet"

# Set the address of the hyperdrive pool
# hyperdrive_address = "0x0000000000000000000000000000000000000000"

# Alternatively, look up the list of registered hyperdrive pools
# This is the registry address deployed on sepolia.
# registry_address = "0xba5156E697d39a03EDA824C19f375383F6b759EA"
#
# hyperdrive_address = Hyperdrive.get_hyperdrive_addresses_from_registry(chain, registry_address)["sdai_14_day"]

# For this example, we launch a chain and local hyperdrive, and set the rpc_uri and hyperdrive address from these.
local_chain = LocalChain()
local_hyperdrive = LocalHyperdrive(local_chain)
rpc_uri = local_chain.rpc_uri
hyperdrive_address = local_hyperdrive.hyperdrive_address

# Need to set different db port here to avoid port collisions with local chain
chain = Chain(rpc_uri, config=Chain.Config(db_port=1234))
hyperdrive_config = Hyperdrive.Config()
hyperdrive_pool = Hyperdrive(chain, hyperdrive_address, hyperdrive_config)

# %%

# We set the private key here. In practice, this would be in a private
# env file somewhere, and we only access this through environment variables.
# For now, we generate a random key and explicitly fund it
private_key = make_private_key()

# Init from private key and attach policy
# This ties the hyperdrive_agent to the hyperdrive_pool here.
# We can connect to another hyperdrive pool and create a separate
# agent object using the same private key, but the underlying wallet
# object would then be out of date if both agents are making trades.
# TODO add registry of public key to the chain object, preventing this from happening
agent0 = hyperdrive_pool.init_agent(
    private_key=private_key,
    policy=PolicyZoo.random,
    # The configuration for the underlying policy
    policy_config=PolicyZoo.random.Config(rng_seed=123),
)

# %%
# We expose this function for testing purposes, but the underlying function calls `mint` and `anvil_set_balance`,
# which are likely to fail on any non-test network.
agent0.add_funds(base=FixedPoint(100000), eth=FixedPoint(100))

# Set max approval
agent0.set_max_approval()

# %%

# Make trades
# Return values here mirror the various events emitted from these contract calls
# These functions are blocking, but relatively easy to expose async versions of the
# trades below
open_long_event = agent0.open_long(base=FixedPoint(11111))
close_long_event = agent0.close_long(maturity_time=open_long_event.maturity_time, bonds=open_long_event.bond_amount)


# %%
random_trade_events = []
for i in range(10):
    # NOTE Since a policy can execute multiple trades per action, the output events is a list
    trade_events: list = agent0.execute_policy_action()
    random_trade_events.extend(trade_events)


# %%

# Analysis

agent_positions = agent0.get_positions()
agent_trade_events = agent0.get_trade_events()
