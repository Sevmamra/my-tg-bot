from caption_parser import parser as caption_parser
import re
import datetime

class TitleProcessor:
    """
    Wraps CaptionParser to produce useful metadata for worker:
    - cleaned title
    - short_title (for thumbnails)
    - safe_filename (for saving files)
    - generated timestamp
    """

    def __init__(self, max_thumb_chars=45):
        # Maximum chars to use on thumbnail (keeps layout clean)
        self.max_thumb_chars = max_thumb_chars

    def make_short_title(self, title: str) -> str:
        """
        Return a shortened version of title suitable for thumbnail text.
        Tries to keep whole words; if too long, truncates with ellipsis.
        """
        if not title:
            return "Untitled"
        t = title.strip()
        if len(t) <= self.max_thumb_chars:
            return t
        # Try to cut at last space before max_thumb_chars
        cut = t[:self.max_thumb_chars]
        last_space = cut.rfind(" ")
        if last_space > int(self.max_thumb_chars * 0.6):
            cut = cut[:last_space]
        return cut.rstrip() + "..."

    def make_safe_filename(self, title: str, ext="mp4", prefix=None):
        """
        Produce a filename-safe string using CaptionParser.sanitize_filename.
        Optionally add a prefix and timestamp to avoid collisions.
        """
        safe = caption_parser.sanitize_filename(title)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        parts = []
        if prefix:
            parts.append(re.sub(r'[^A-Za-z0-9_\-]', '', str(prefix)))
        parts.append(safe if safe else "untitled")
        parts.append(timestamp)
        filename = "_".join(parts) + f".{ext}"
        return filename

    def process(self, raw_caption: str, owner_name: str = "Owner", prefix=None):
        """
        Main entrypoint.
        Returns a dict:
        {
            'title': 'Clean Full Title',
            'short_title': 'Short title for thumb',
            'safe_filename': 'file_name.mp4',
            'owner': owner_name,
            'generated_at': '2025-11-15T12:34:56'  # ISO format
        }
        """
        clean_title = caption_parser.extract_title(raw_caption)
        short_title = self.make_short_title(clean_title)
        safe_filename = self.make_safe_filename(clean_title, ext="mp4", prefix=prefix)
        return {
            "title": clean_title,
            "short_title": short_title,
            "safe_filename": safe_filename,
            "owner": owner_name,
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
        }

# global instance
title_processor = TitleProcessor()
