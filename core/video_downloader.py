import os
import re
import requests
from bs4 import BeautifulSoup

class VideoDownloader:

    def __init__(self):
        # Folder to store downloaded videos
        self.download_dir = "downloads"
        os.makedirs(self.download_dir, exist_ok=True)

    def sanitize_filename(self, text):
        return re.sub(r'[^a-zA-Z0-9_-]', '_', text)

    def download_instagram_video(self, url: str):
        """
        FREE method using Instagram's open graph tags.
        Works only for PUBLIC reels.
        """

        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X)"
        }

        try:
            html = requests.get(url, headers=headers).text
        except:
            return None, "Unable to access Instagram (maybe downtime)."

        soup = BeautifulSoup(html, "html.parser")

        # Look for video URL inside <meta property="og:video">
        meta = soup.find("meta", property="og:video")
        if not meta:
            return None, "Video link not found. Maybe it's private?"

        video_url = meta.get("content")

        # Prepare local file path
        filename = self.sanitize_filename(url.split("/")[-2]) + ".mp4"
        filepath = os.path.join(self.download_dir, filename)

        # Download video
        try:
            r = requests.get(video_url, stream=True)
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        except:
            return None, "Error downloading the video."

        return filepath, None


# Global instance
downloader = VideoDownloader()
