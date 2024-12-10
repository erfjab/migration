from .system_config import SystemConfig

logger = SystemConfig.setup_logger()

try:
    config = SystemConfig.check_required_settings()
except ValueError as e:
    logger.error(f"Configuration error: {str(e)}")
    raise

from .panel import MarzneshinClient  # noqa: E402

__all__ = ["MarzneshinClient"]