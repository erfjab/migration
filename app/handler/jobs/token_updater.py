from utils import panel
from utils.log import logger
from models import TokenUpsert
from db.crud import TokenManager


async def token_update() -> bool:
    """Add or update MARZNESHIN panel token every X time."""
    try:
        get_token = await panel.get_token()

        if get_token:
            token_data = await TokenManager.upsert(TokenUpsert(token=get_token))
            if token_data:
                logger.info("Token updated successfully.")
                return True
            else:
                logger.error("Failed to update token in database.")
                return False

        logger.error("Failed to retrieve token: No token received.")
        return False

    except Exception as e:
        logger.error(f"An unexpected 'TOKEN_UPDATE' error occurred: {str(e)}")
        return False
