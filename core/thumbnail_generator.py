from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import os

class ThumbnailGenerator:
    def __init__(self):
        # Folder to save thumbnails
        self.output_dir = "thumbnails"
        os.makedirs(self.output_dir, exist_ok=True)

        # Safe fallback font (comes with Pillow)
        self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    def create_gradient_background(self, width=1280, height=720):
        """
        Creates a smooth vertical gradient (2 random colors)
        """
        color1 = tuple(random.randint(80, 160) for _ in range(3))
        color2 = tuple(random.randint(160, 240) for _ in range(3))

        img = Image.new("RGB", (width, height), color1)
        draw = ImageDraw.Draw(img)

        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        return img

    def wrap_text(self, text, font, max_width):
        """
        Wrap text to fit thumbnail width
        """
        lines = []
        words = text.split()

        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font.getlength(test_line) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def generate_thumbnail(self, title: str, filename: str):
        """
        Full process:
        - Gradient background
        - Big title text centered
        - Image saved in thumbnails/
        """

        width = 1280
        height = 720

        # Background
        img = self.create_gradient_background(width, height)
        draw = ImageDraw.Draw(img)

        # Main title font
        font = ImageFont.truetype(self.font_path, 72)

        # Text margins
        max_width = width - 200

        # Wrapped lines
        lines = self.wrap_text(title, font, max_width)

        total_text_height = len(lines) * 85
        start_y = (height - total_text_height) // 2

        # Draw lines
        for i, line in enumerate(lines):
            line_width = font.getlength(line)
            x = (width - line_width) // 2
            y = start_y + i * 85

            # Shadow
            draw.text((x+4, y+4), line, fill="black", font=font)
            # Actual text
            draw.text((x, y), line, fill="white", font=font)

        # Save
        output_path = os.path.join(self.output_dir, f"{filename}.png")
        img.save(output_path)

        return output_path


# Global instance
thumbnailer = ThumbnailGenerator()
