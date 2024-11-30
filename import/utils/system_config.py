from decouple import config
import re
import logging


class SystemConfig:
    _instance = None
    _logger = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def setup_logger(
        bot_name: str = "MarzneshinMigration-Import", level: int = logging.INFO
    ) -> logging.Logger:
        if SystemConfig._logger is None:
            logger = logging.getLogger(bot_name)
            logger.setLevel(level)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)

            file_handler = logging.FileHandler(f"{bot_name}.log")
            file_handler.setLevel(logging.INFO)

            formatter = logging.Formatter("%(levelname)-8s | %(message)s")
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)

            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

            SystemConfig._logger = logger

        return SystemConfig._logger

    @staticmethod
    def get_config() -> "ConfigData":
        return ConfigData(
            MARZNESHIN_USERNAME=config("MARZNESHIN_USERNAME", default="", cast=str),
            MARZNESHIN_PASSWORD=config("MARZNESHIN_PASSWORD", default="", cast=str),
            MARZNESHIN_ADDRESS=config("MARZNESHIN_ADDRESS", default="", cast=str),
            MARZBAN_USERS_DATA=config(
                "MARZBAN_USERS_DATA", default="marzban.json", cast=str
            ),
            USERNAME_SUFFIX=config("USERNAME_SUFFIX", default=2, cast=int)
        )

    @staticmethod
    def check_required_settings() -> "ConfigData":
        settings = SystemConfig.get_config()

        required_settings = {
            "MARZNESHIN_USERNAME": "The 'MARZNESHIN_USERNAME' setting is required and cannot be empty.",
            "MARZNESHIN_PASSWORD": "The 'MARZNESHIN_PASSWORD' setting is required and cannot be empty.",
            "MARZNESHIN_ADDRESS": "The 'MARZNESHIN_ADDRESS' setting is required and cannot be empty.",
        }

        for setting_name, error_message in required_settings.items():
            if not getattr(settings, setting_name):
                raise ValueError(error_message)

        address_pattern = re.compile(
            r"^(https?:\/\/)"
            r"((([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})"
            r"|(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))"
            r":\d{1,5}$"
        )

        if not address_pattern.match(settings.MARZNESHIN_ADDRESS):
            raise ValueError(
                "The 'MARZNESHIN_ADDRESS' setting must be a valid URL with format like 'https://sub.domain.com:port' or 'http://ip:port'."
            )

        return settings


class ConfigData:
    def __init__(
        self,
        MARZNESHIN_USERNAME: str,
        MARZNESHIN_PASSWORD: str,
        MARZNESHIN_ADDRESS: str,
        MARZBAN_USERS_DATA: str,
    ):
        self.MARZNESHIN_USERNAME = MARZNESHIN_USERNAME
        self.MARZNESHIN_PASSWORD = MARZNESHIN_PASSWORD
        self.MARZNESHIN_ADDRESS = MARZNESHIN_ADDRESS
        self.MARZBAN_USERS_DATA = MARZBAN_USERS_DATA
