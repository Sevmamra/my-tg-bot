import re

class CaptionParser:
    """
    Takes raw caption and extracts a clean title.
    Useful for thumbnails & consistent naming.
    """

    @staticmethod
    def extract_title(caption: str) -> str:
        """
        Extracts a clean title from the raw caption.
        Steps:
        - Remove URLs
        - Remove emojis
        - Remove hashtags
        - Remove parentheses/brackets content
        - Remove extra spaces
        """

        if not caption or caption.strip() == "":
            return "Untitled"

        text = caption

        # ---------------------------
        # Remove URLs
        # ---------------------------
        text = re.sub(r'https?://\S+', '', text)

        # ---------------------------
        # Remove emojis
        # ---------------------------
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002700-\U000027BF"  # dingbats
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols
            "\U00002600-\U000026FF"  # Misc symbols
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub('', text)

        # ---------------------------
        # Remove hashtags
        # ---------------------------
        text = re.sub(r'#\w+', '', text)

        # ---------------------------
        # Remove brackets and content inside
        # Example: "Test Video (2024)" -> "Test Video"
        # ---------------------------
        text = re.sub(r'\(.*?\)', '', text)
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\{.*?\}', '', text)

        # ---------------------------
        # Remove any non-word chars except space, dash
        # ---------------------------
        text = re.sub(r'[^a-zA-Z0-9\s\-]', '', text)

        # ---------------------------
        # Normalize spaces
        # ---------------------------
        text = re.sub(r'\s+', ' ', text).strip()

        # ---------------------------
        # If empty after cleaning
        # ---------------------------
        if text == "":
            return "Untitled"

        # ---------------------------
        # Limit title length (Thumbnail safety)
        # ---------------------------
        if len(text) > 60:
            text = text[:57] + "..."

        return text

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """
        Convert title into a safe filename for saving.
        """
        name = name.strip()
        name = name.replace(" ", "_")
        name = re.sub(r'[^a-zA-Z0-9_\-]', '', name)
        if len(name) > 80:
            name = name[:80]
        return name


# Global instance for convenience
parser = CaptionParser()
