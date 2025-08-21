import os
import sys

# import tomllib
from decouple import Config, RepositoryEnv, config
from loguru import logger

## Logging setup
logger.remove()
logger.add(sys.stdout, colorize=True, format="{level} | {message}")

## Control switch for production and dev configurations
# User specifies custom env var set to use on startup, else errors out at loading 'templates'
env_path = os.environ.get("ENV_PATH")
if env_path is not None:
    logger.debug(
        f"ENV_PATH specified. Running from environment variables in {env_path}..."
    )
    config = Config(RepositoryEnv(env_path))
else:
    logger.debug(
        "ENV_PATH not specified, running from manually set environment variables..."
    )

# with open("pyproject.toml", "rb") as f:
#     pypro = tomllib.load(f)


## Settings class to store decoupled instance and build settings:
class Settings:
    def __init__(self):
        # self.version = pypro["tool"]["poetry"]["version"]

        # Knowledge settings
        self.meas_period = config("meas_period", cast=int, default=1)
        self.manifest = config("manifest", cast=str, default=None)
        self.mpm = config("mpm", cast=str, default=None)
        self.default_preferences = config("default_preferences", cast=str, default=None)

        self.preferences = config("preferences", cast=str, default=None)
        self.history = config("history", cast=str, default=None)

        # Instance settings
        self.log_level = config(
            "log_level", cast=str, default="WARNING"
        )  # Logging level for instance
        self.generate_image = config(
            "generate_image", cast=bool, default=True
        )  # Generate image flag (pictoraless)
        self.cache_image = config(
            "cache_image", cast=bool, default=False
        )  # Cache generated image flag
        self.outputs = config(
            "outputs", cast=bool, default=False
        )  # Logging of intermediate files
        self.performance_month = config(
            "performance_month", cast=str, default=""
        )  # performance_month for instance
        self.use_mi = config("use_mi", cast=bool, default=True)  # use mi
        self.use_preferences = config(
            "use_preferences", cast=bool, default=True
        )  # use preferences
        self.use_history = config("use_history", cast=bool, default=True)  # use history
        self.use_coachiness = config(
            "use_coachiness", cast=bool, default=True
        )  # use coachiness

        # Instance display settings
        self.display_window = config("display_window", cast=int, default=6)
        self.plot_goal_line = config("plot_goal_line", cast=bool, default=True)


# Instantiate
settings = Settings()
