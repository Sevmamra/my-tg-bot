import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from config.settings import Settings
from core.redis_queue import queue
from core.title_processor import title_processor

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# -------------------------------------------------------
# START COMMAND
# -------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Settings.OWNER_ID:
        return await update.message.reply_text("❌ You are not authorized.")

    await update.message.reply_text(
        "✅ Bot is active.\n\n"
        "Send me videos or PDFs and I will process them automatically."
    )


# -------------------------------------------------------
# SET TARGET GROUP & TOPIC
# -------------------------------------------------------
async def set_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /setgroup -100xxxxx 12345
    group_id + topic_id
    """
    if update.effective_user.id != Settings.OWNER_ID:
        return await update.message.reply_text("❌ You are not authorized.")

    try:
        group_id = int(context.args[0])
        topic_id = int(context.args[1])
    except:
        return await update.message.reply_text(
            "Usage:\n/setgroup <group_id> <topic_id>"
        )

    Settings.TARGET_GROUP_ID = group_id
    Settings.TARGET_TOPIC_ID = topic_id

    await update.message.reply_text(
        f"🔗 Target updated:\nGroup: {group_id}\nTopic: {topic_id}"
    )


# -------------------------------------------------------
# HANDLE RECEIVED VIDEO/PDF
# -------------------------------------------------------
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Settings.OWNER_ID:
        return await update.message.reply_text("❌ You are not authorized.")

    msg = update.message

    file_type = None
    file_id = None

    # VIDEO
    if msg.video:
        file_type = "video"
        file_id = msg.video.file_id

    # DOCUMENT (PDF)
    elif msg.document:
        if msg.document.mime_type == "application/pdf":
            file_type = "pdf"
            file_id = msg.document.file_id

    if not file_type:
        return await msg.reply_text("❌ Send only video or PDF.")

    raw_caption = msg.caption or "Untitled"

    # 🔥 process title
    meta = title_processor.process(raw_caption, owner_name="Nishit")

    # push into redis queue
    queue.push({
        "file_id": file_id,
        "file_type": file_type,
        "raw_caption": raw_caption,
        "title": meta["title"],
        "short_title": meta["short_title"],
        "safe_filename": meta["safe_filename"],
        "owner_id": update.effective_user.id,
    })

    await msg.reply_text(
        f"📥 Added to queue\n\n"
        f"Title: {meta['title']}\n"
        f"Short: {meta['short_title']}\n"
        f"Filename: {meta['safe_filename']}\n"
        f"Queue size: {queue.size()}"
    )


# -------------------------------------------------------
# CLEAR QUEUE
# -------------------------------------------------------
async def clear_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != Settings.OWNER_ID:
        return

    queue.clear()
    await update.message.reply_text("🗑 Queue cleared!")


# -------------------------------------------------------
# BOT APPLICATION
# -------------------------------------------------------
def main():
    app = ApplicationBuilder().token(Settings.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setgroup", set_target))
    app.add_handler(CommandHandler("clear_queue", clear_queue))

    app.add_handler(
        MessageHandler(
            filters.VIDEO | filters.Document.PDF,
            handle_file
        )
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
