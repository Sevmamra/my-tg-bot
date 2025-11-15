import os

class Settings:
    """
    Loads all required configuration from environment variables.
    These will be added inside Render Dashboard → Environment.
    """

    # ---------------------------------------------------
    # TELEGRAM
    # ---------------------------------------------------
    BOT_TOKEN = os.getenv("BOT_TOKEN")  # Telegram Bot Token
    OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # Your Telegram User ID

    # ---------------------------------------------------
    # REDIS (Render Free Redis)
    # ---------------------------------------------------
    REDIS_URL = os.getenv("REDIS_URL")  # Example: redis://default:pass@host:6379

    # ---------------------------------------------------
    # TARGET GROUP / TOPIC
    # Bot owner sets these with Telegram commands
    # They remain None until configured
    # ---------------------------------------------------
    TARGET_GROUP_ID = None
    TARGET_TOPIC_ID = None

    # ---------------------------------------------------
    # LOCAL DIRECTORIES FOR TEMP STORAGE
    # Render ephemeral disk usable for video + thumbnail
    # ---------------------------------------------------
    BASE_DIR = "/tmp/bot_files"
    VIDEO_DIR = f"{BASE_DIR}/videos"
    THUMB_DIR = f"{BASE_DIR}/thumbs"

    @staticmethod
    def ensure_folders():
        """Create necessary temp folders on start."""
        os.makedirs(Settings.VIDEO_DIR, exist_ok=True)
        os.makedirs(Settings.THUMB_DIR, exist_ok=True)


# Prepare folders immediately on import
Settings.ensure_folders()
