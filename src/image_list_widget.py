"""PyQt5 list widget that accepts drag-and-drop of image and PDF files."""
from pathlib import Path

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import (
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QImage,
    QPixmap,
)
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QSizePolicy

# Supported file extensions (images + PDF)
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff", ".tif"}
PDF_EXTENSIONS = {".pdf"}
SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | PDF_EXTENSIONS


def is_supported_path(path: str) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS


class ImageListWidget(QListWidget):
    """List widget that accepts drag-and-drop of image files and shows thumbnails."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setIconSize(QSize(72, 72))
        self.setSpacing(4)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(120)

    def dragEnterEvent(self, event: QDragEnterEvent):
        # 외부 파일 추가(URL) 또는 목록 내 순서 변경(같은 위젯에서 드래그)
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        elif event.source() is self:
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        elif event.source() is self:
            event.setDropAction(Qt.MoveAction)
            event.accept()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            for url in event.mimeData().urls():
                try:
                    if url.isLocalFile():
                        path = url.toLocalFile()
                        if path and is_supported_path(path):
                            self._add_item(path)
                except Exception:
                    pass
        else:
            # 목록 내 드래그: 순서 변경
            super().dropEvent(event)

    def _pdf_first_page_thumbnail(self, path: str) -> QPixmap:
        """Render first page of PDF as thumbnail. Returns null QPixmap on failure."""
        try:
            import fitz
            doc = fitz.open(path)
            try:
                if len(doc) == 0:
                    return QPixmap()
                page = doc[0]
                mat = fitz.Matrix(0.15, 0.15)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                if not pix.samples or pix.width <= 0 or pix.height <= 0:
                    return QPixmap()
                # Qt가 버퍼를 참조만 하므로, doc.close() 전에 bytes 복사해서 전달
                data = bytes(pix.samples)
                stride = getattr(pix, "stride", pix.width * pix.n)
                qimg = QImage(
                    data,
                    pix.width,
                    pix.height,
                    stride,
                    QImage.Format_RGB888,
                )
                if qimg.isNull():
                    return QPixmap()
                thumb = QPixmap.fromImage(qimg).scaled(
                    72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                return thumb
            finally:
                doc.close()
        except Exception:
            pass
        return QPixmap()

    def _add_item(self, path: str):
        item = QListWidgetItem(self)
        item.setData(Qt.UserRole, path)
        item.setText(Path(path).name)
        try:
            if Path(path).suffix.lower() == ".pdf":
                # PDF: 목록에는 파일명만 표시 (드롭 시 썸네일 렌더링으로 앱 크래시 방지)
                thumb = QPixmap()
            else:
                thumb = QPixmap(path)
            if not thumb.isNull():
                icon = thumb.scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                item.setIcon(icon)
        except Exception:
            pass
        self.addItem(item)

    def add_paths(self, paths: list):
        for path in paths:
            if is_supported_path(path):
                self._add_item(path)

    def get_paths(self) -> list:
        paths = []
        for i in range(self.count()):
            item = self.item(i)
            path = item.data(Qt.UserRole)
            if path:
                paths.append(path)
        return paths
