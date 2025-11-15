import os
import time
import logging
import asyncio
import ffmpeg
from telegram import Bot
from config.settings import Settings
from core.redis_queue import queue
from core.title_processor import title_processor
from core.thumbnail_generator import thumb
from core.video_downloader import downloader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - WORKER - %(levelname)s - %(message)s"
)

bot = Bot(token=Settings.TELEGRAM_BOT_TOKEN)

class Worker:

    async def download_telegram_file(self, file_id, local_path):
        """Download Telegram file from file_id and save locally."""
        f = await bot.get_file(file_id)
        await f.download_to_drive(local_path)

    def merge_thumbnail_with_video(self, video_path, thumbnail_path, output_path):
        """
        Set custom thumbnail for video using ffmpeg.
        """
        try:
            (
                ffmpeg
                .input(video_path)
                .output(output_path, vcodec="copy", acodec="copy", **{'attach': thumbnail_path})
                .overwrite_output()
                .run(quiet=True)
            )
            return True
        except Exception as e:
            logging.error(f"FFmpeg error: {e}")
            return False

    async def send_to_group(self, file_path, caption, file_type):
        """Send processed file to target group/topic."""
        try:
            if file_type == "video":
                await bot.send_video(
                    chat_id=Settings.TARGET_GROUP_ID,
                    message_thread_id=Settings.TARGET_TOPIC_ID,
                    video=open(file_path, "rb"),
                    caption=caption,
                    supports_streaming=True
                )
            else:
                await bot.send_document(
                    chat_id=Settings.TARGET_GROUP_ID,
                    message_thread_id=Settings.TARGET_TOPIC_ID,
                    document=open(file_path, "rb"),
                    caption=caption
                )
        except Exception as e:
            logging.error(f"Send error: {e}")

    async def process_job(self, job):
        """
        Process a single job from Redis queue.
        """
        file_id = job["file_id"]
        file_type = job["file_type"]
        raw_caption = job["raw_caption"]
        title = job["title"]
        short_title = job["short_title"]
        safe_filename = job["safe_filename"]

        # Paths
        input_path = f"temp/{safe_filename}"
        os.makedirs("temp", exist_ok=True)

        # STEP 1: Download file from Telegram
        logging.info(f"Downloading file: {safe_filename}")
        await self.download_telegram_file(file_id, input_path)

        # STEP 2: Generate THUMBNAIL
        logging.info("Generating thumbnail...")
        thumbnail_path = thumb.generate(short_title, safe_filename.replace(".mp4", ".jpg"))

        # STEP 3: Merge thumbnail with video
        output_path = f"final/{safe_filename}"
        os.makedirs("final", exist_ok=True)

        if file_type == "video":
            logging.info("Merging thumbnail into video...")
            self.merge_thumbnail_with_video(input_path, thumbnail_path, output_path)
        else:
            output_path = input_path  # PDFs don’t need ffmpeg

        # STEP 4: Send to group
        caption_text = f"🎬 {title}"
        logging.info("Sending processed file to Telegram group/topic...")
        await self.send_to_group(output_path, caption_text, file_type)

        # STEP 5: Cleanup
        try:
            os.remove(input_path)
        except:
            pass

        logging.info("Job completed.\n\n")

    async def run(self):
        """Continuous loop worker."""
        logging.info("Worker started...")

        while True:
            job = queue.pop()

            if job:
                logging.info(f"Job found: {job['title']}")
                try:
                    await self.process_job(job)
                except Exception as e:
                    logging.error(f"Job failed: {e}")
            else:
                await asyncio.sleep(2)  # No job, small rest


if __name__ == "__main__":
    worker = Worker()
    asyncio.run(worker.run())
