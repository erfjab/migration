from decouple import config
import re


# Configuration settings
def check_required_settings():
    settings = {
        "MARZNESHIN_USERNAME": MARZNESHIN_USERNAME,
        "MARZNESHIN_PASSWORD": MARZNESHIN_PASSWORD,
        "MARZNESHIN_ADDRESS": MARZNESHIN_ADDRESS,
        "MARZBAN_JWT_TOKEN": MARZBAN_JWT_TOKEN,
        "MARZBAN_XRAY_SUBSCRIPTION_PATH": MARZBAN_XRAY_SUBSCRIPTION_PATH,
    }

    # Address pattern: Supports https://domain:port or http://ip:port
    address_pattern = re.compile(
        r"^(https?:\/\/)"  # http or https
        r"((([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})"  # domain (sub.domain.com or domain.com)
        r"|(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))"  # or IP address
        r":\d{1,5}$"  # port number
    )

    for setting_name, value in settings.items():
        if not value:
            raise ValueError(
                f"The '{setting_name}' setting is required and cannot be empty."
            )

    # Validate MARZNESHIN_ADDRESS format
    if not address_pattern.match(MARZNESHIN_ADDRESS):
        raise ValueError(
            "The 'MARZNESHIN_ADDRESS' setting must be a valid URL with format like 'https://sub.domain.com:port' or 'http://ip:port'."
        )


UVICORN_HOST = config("UVICORN_HOST", default="0.0.0.0")
UVICORN_PORT = config("UVICORN_PORT", cast=int, default=999)
UVICORN_UDS = config("UVICORN_UDS", default=None)
UVICORN_SSL_CERTFILE = config("UVICORN_SSL_CERTFILE", default=None)
UVICORN_SSL_KEYFILE = config("UVICORN_SSL_KEYFILE", default=None)
DOCS = config("DOCS", default=True, cast=bool)
DEBUG = config("DEBUG", default=False, cast=bool)

# MARZNESHIN Panel Settings
MARZNESHIN_USERNAME = config("MARZNESHIN_USERNAME", default="", cast=str)
MARZNESHIN_PASSWORD = config("MARZNESHIN_PASSWORD", default="", cast=str)
MARZNESHIN_ADDRESS = config("MARZNESHIN_ADDRESS", default="", cast=str)
MARZBAN_JWT_TOKEN = config("MARZBAN_JWT_TOKEN", default="", cast=str)
MARZBAN_XRAY_SUBSCRIPTION_PATH = config(
    "MARZBAN_XRAY_SUBSCRIPTION_PATH", default="", cast=str
)
USERNAME_SUFFIX = config("USERNAME_SUFFIX", default=2, cast=int)