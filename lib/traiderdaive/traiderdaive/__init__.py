"""The gym environments for hyperdrive. Also registers the environment to gym."""

from gymnasium.envs.registration import register

from .gym_environments.simple_hyperdrive_env import SimpleHyperdriveEnv

# Register simple hyperdrive env to gym
register(
    id="traiderdaive/simple_hyperdrive_env",
    entry_point="traiderdaive.gym_environments.simple_hyperdrive_env:SimpleHyperdriveEnv",
    max_episode_steps=300,
)
