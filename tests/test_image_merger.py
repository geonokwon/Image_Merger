"""Tests for image_merger module."""
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from src.image_merger import (
    MergeDirection,
    load_images,
    merge_images,
)


@pytest.fixture
def temp_image_10x10():
    """Create a temporary 10x10 PNG."""
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name)
        yield f.name
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def temp_image_20x20():
    """Create a temporary 20x20 PNG."""
    img = Image.new("RGB", (20, 20), color=(0, 255, 0))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img.save(f.name)
        yield f.name
    Path(f.name).unlink(missing_ok=True)


def test_load_images_returns_list(temp_image_10x10):
    labeled = load_images([temp_image_10x10])
    assert len(labeled) == 1
    label, img = labeled[0]
    assert img.size == (10, 10)
    assert label  # filename stem


def test_load_images_skips_missing():
    labeled = load_images(["/nonexistent/path.png"])
    assert len(labeled) == 0


def test_load_images_multiple(temp_image_10x10, temp_image_20x20):
    labeled = load_images([temp_image_10x10, temp_image_20x20])
    assert len(labeled) == 2
    assert labeled[0][1].size == (10, 10)
    assert labeled[1][1].size == (20, 20)


def test_merge_images_vertical(temp_image_10x10, temp_image_20x20):
    labeled = load_images([temp_image_10x10, temp_image_20x20])
    result = merge_images(labeled, direction=MergeDirection.VERTICAL)
    # grid: 1 row with 2 blocks, block width = img.width (10, 20), label_height=44
    assert result.width == 10 + 20
    assert result.height == max(44 + 10, 44 + 20)


def test_merge_images_horizontal(temp_image_10x10, temp_image_20x20):
    labeled = load_images([temp_image_10x10, temp_image_20x20])
    result = merge_images(labeled, direction=MergeDirection.HORIZONTAL)
    assert result.width == 10 + 20
    assert result.height == max(44 + 10, 44 + 20)


def test_merge_images_with_spacing(temp_image_10x10):
    labeled = load_images([temp_image_10x10, temp_image_10x10])
    result = merge_images(labeled, direction=MergeDirection.VERTICAL, spacing=5)
    # 1 row, 2 blocks: width = 10+5+10, height = max(54,54)=54
    assert result.width == 10 + 5 + 10
    assert result.height == 44 + 10


def test_merge_images_empty_raises():
    with pytest.raises(ValueError, match="No images to merge"):
        merge_images([])


@pytest.fixture
def temp_pdf_one_page():
    """Create a minimal 1-page PDF."""
    try:
        import fitz
    except ImportError:
        pytest.skip("PyMuPDF not installed")
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name
    try:
        doc = fitz.open()
        doc.new_page(width=100, height=100)
        doc.save(path)
        doc.close()
        yield path
    finally:
        Path(path).unlink(missing_ok=True)


def test_load_images_pdf(temp_pdf_one_page):
    labeled = load_images([temp_pdf_one_page])
    assert len(labeled) == 1
    _, img = labeled[0]
    assert img.size[0] > 0 and img.size[1] > 0


def test_load_images_mixed(temp_image_10x10, temp_pdf_one_page):
    labeled = load_images([temp_image_10x10, temp_pdf_one_page])
    assert len(labeled) == 2
    assert labeled[0][1].size == (10, 10)
