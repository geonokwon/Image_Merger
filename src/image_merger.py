"""Image merge logic - combines multiple images into one. Supports images and PDF (pages as images)."""
import os
import sys
from pathlib import Path
from enum import Enum
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFont

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


class MergeDirection(str, Enum):
    """Direction to stack images."""
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


def _load_pdf_pages(path: str, dpi: int = 150) -> List[Image.Image]:
    """Render each PDF page to a PIL Image. Returns empty list if PDF cannot be opened."""
    if fitz is None:
        return []
    images = []
    try:
        doc = fitz.open(path)
        try:
            for i in range(len(doc)):
                page = doc[i]
                mat = fitz.Matrix(dpi / 72, dpi / 72)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                data = bytes(pix.samples)
                pil_img = Image.frombytes("RGB", (pix.width, pix.height), data)
                images.append(pil_img.convert("RGBA"))
        finally:
            doc.close()
    except Exception:
        pass
    return images


def _resize_to_max(img: Image.Image, max_side: int) -> Image.Image:
    """Resize image so the longer side is at most max_side; keep aspect ratio. Returns copy."""
    w, h = img.size
    if max_side <= 0 or (w <= max_side and h <= max_side):
        return img.copy()
    if w >= h:
        new_w = max_side
        new_h = max(1, int(h * max_side / w))
    else:
        new_h = max_side
        new_w = max(1, int(w * max_side / h))
    return img.resize((new_w, new_h), Image.Resampling.LANCZOS)


def load_images(paths: List[str]) -> List[Tuple[str, Image.Image]]:
    """
    Load (label, image) from file paths.
    Label = filename without extension. PDF pages: "stem (1)", "stem (2)", ...
    """
    labeled: List[Tuple[str, Image.Image]] = []
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        stem = p.stem
        suffix = p.suffix.lower()
        if suffix == ".pdf":
            pages = _load_pdf_pages(path)
            for i, img in enumerate(pages, 1):
                label = f"{stem} ({i})" if len(pages) > 1 else stem
                labeled.append((label, img))
            continue
        try:
            img = Image.open(p).convert("RGBA")
            labeled.append((stem, img))
        except Exception:
            continue
    return labeled


def _default_font(size: int = 14, bold: bool = False):
    """Try to load a readable font (UTF-8/한글 가능); bold first if requested, then regular, then default.
    On Windows/CI we avoid calling getbbox() in _make_labeled_block; here we still try Arial etc. for UTF-8.
    """
    bold_paths = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",  # index 1 is often bold
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    )
    regular_paths = (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for path in (bold_paths if bold else regular_paths):
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    if bold:
        for path in regular_paths:
            try:
                return ImageFont.truetype(path, size)
            except (OSError, IOError):
                continue
    return ImageFont.load_default()


def _make_labeled_block(
    label: str,
    img: Image.Image,
    label_height: int = 64,
    padding: int = 10,
    bg_color: tuple = (255, 255, 255, 255),
    text_color: tuple = (0, 0, 0, 255),
) -> Image.Image:
    """Create one block: label at top-left (bold, larger), image below. Block width = image width."""
    font = _default_font(38, bold=True)
    max_label_w = max(img.width - padding * 2, 80)
    # On Windows or in CI, font.getbbox() can block in headless; use estimate (~10px/char, 24px height for size 38).
    use_estimate = sys.platform == "win32" or os.environ.get("CI") == "true"
    if use_estimate:
        approx_char_w, approx_text_h = 10, 24
        label_w = len(label) * approx_char_w + padding * 2
        if label_w > max_label_w:
            n = max(1, (max_label_w - padding * 2 - 8) // approx_char_w)  # 8 for "…"
            label = (label[:n] + "…") if len(label) > n else label
        text_y = (label_height - approx_text_h) // 2
    else:
        try:
            bbox = font.getbbox(label)
            label_w = bbox[2] - bbox[0] + padding * 2
            if label_w > max_label_w:
                while label_w > max_label_w and len(label) > 1:
                    label = label[:-1] + "…"
                    bbox = font.getbbox(label)
                    label_w = bbox[2] - bbox[0] + padding * 2
        except Exception:
            if len(label) * 18 > max_label_w:
                label = label[: max(1, max_label_w // 18)] + "…"
        try:
            bbox = font.getbbox(label)
            text_h = bbox[3] - bbox[1]
            text_y = (label_height - text_h) // 2
        except Exception:
            text_y = 8
    block_w = img.width
    block_h = label_height + img.height
    block = Image.new("RGBA", (block_w, block_h), bg_color)
    draw = ImageDraw.Draw(block)
    draw.text((padding, text_y), label, font=font, fill=text_color)
    block.paste(img, (0, label_height))
    # Black outline so "this image = this filename" is clear
    draw.rectangle(
        [(0, 0), (block_w - 1, block_h - 1)],
        outline=(0, 0, 0, 255),
        width=1,
    )
    return block


def merge_images(
    labeled_items: List[Tuple[str, Image.Image]],
    direction: MergeDirection = MergeDirection.VERTICAL,
    spacing: int = 0,
    label_height: int = 64,
    cols_per_row: int = 3,
    background_color: tuple = (255, 255, 255, 255),
    max_image_size: int = 0,
) -> Image.Image:
    """
    Merge (label, image) blocks into one. Layout: up to 3 blocks per row (가로 3개), then next row.
    Each block = label at top-left, image below. Block width = image width.
    If max_image_size > 0, each image is resized so its longer side is at most that (keeps aspect ratio).
    """
    if not labeled_items:
        raise ValueError("No images to merge")

    if max_image_size > 0:
        labeled_items = [(label, _resize_to_max(img, max_image_size)) for label, img in labeled_items]

    blocks = [_make_labeled_block(label, img, label_height=label_height) for label, img in labeled_items]

    if len(blocks) == 1:
        return blocks[0]

    # 그리드: 한 줄에 최대 cols_per_row(3)개, 다음 줄 ...
    n = len(blocks)
    rows = [blocks[i : i + cols_per_row] for i in range(0, n, cols_per_row)]
    row_heights = [max(b.height for b in row) for row in rows]
    row_widths = [sum(b.width for b in row) + spacing * (len(row) - 1) for row in rows]
    total_width = max(row_widths)
    total_height = sum(row_heights) + spacing * (len(rows) - 1)

    result = Image.new("RGBA", (total_width, total_height), background_color)
    y = 0
    for row, row_h in zip(rows, row_heights):
        x = 0
        for block in row:
            result.paste(block, (x, y))
            x += block.width + spacing
        y += row_h + spacing
    return result
