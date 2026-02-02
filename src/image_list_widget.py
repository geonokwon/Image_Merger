"""PyQt5 list widget that accepts drag-and-drop of image and PDF files."""
from pathlib import Path

from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import (
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QImage,
    QPixmap,
    QPainter,
    QColor,
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
        self.setDefaultDropAction(Qt.TargetMoveAction)
        self.setDropIndicatorShown(True)
        self.setStyleSheet("""
            QListWidget {
                show-decoration-selected: 1;
            }
        """)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(120)
        self._drop_line_y = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        elif event.source() is self:
            event.acceptProposedAction()
        self._drop_line_y = None
        self.update()

    def dragLeaveEvent(self, event):
        self._drop_line_y = None
        self.update()
        super().dragLeaveEvent(event)

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        elif event.source() is self:
            event.setDropAction(Qt.TargetMoveAction)
            event.accept()
            vp_pos = self.viewport().mapFrom(self, event.pos())
            self._drop_line_y = self._drop_line_y_at(vp_pos)
            self.update()
        else:
            self._drop_line_y = None
            self.update()

    def dropEvent(self, event: QDropEvent):
        self._drop_line_y = None
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
            return
        # 목록 내 순서 변경: Qt 기본 drop 시 항목 사라지는 버그 회피 → 수동 이동
        if event.source() is self:
            event.accept()
            drop_index = self._drop_index_at(self.viewport().mapFrom(self, event.pos()))
            selected = self.selectedItems()
            if not selected:
                return
            item = selected[0]
            row = self.row(item)
            if row < 0:
                return
            taken = self.takeItem(row)
            if taken is None:
                return
            if row < drop_index:
                drop_index -= 1
            self.insertItem(drop_index, taken)
            self.setCurrentItem(taken)
            return
        super().dropEvent(event)

    def _drop_index_at(self, viewport_pos):
        """Return index to insert at: cursor in top half of item → before, bottom half → after."""
        idx = self.indexAt(viewport_pos)
        if not idx.isValid():
            return self.count()
        row = idx.row()
        rect = self.visualItemRect(self.item(row))
        if not rect.isValid():
            return row
        mid_y = rect.top() + rect.height() // 2
        if viewport_pos.y() < mid_y:
            return row
        return row + 1

    def _drop_line_y_at(self, viewport_pos):
        """드롭 위치 선 Y (뷰포트 기준)."""
        idx = self.indexAt(viewport_pos)
        if not idx.isValid():
            if self.count() == 0:
                return 10
            last = self.item(self.count() - 1)
            rect = self.visualItemRect(last)
            return rect.bottom() + 2 if rect.isValid() else None
        row = idx.row()
        rect = self.visualItemRect(self.item(row))
        if not rect.isValid():
            return None
        mid_y = rect.top() + rect.height() // 2
        if viewport_pos.y() < mid_y:
            return rect.top() - 1
        return rect.bottom() + 2

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._drop_line_y is not None:
            pt = self.viewport().mapTo(self, QPoint(0, self._drop_line_y))
            y = pt.y()
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            # 눈에 띄는 드롭 위치: 굵은 선 + 살짝 그림자
            for dx, dy, color in [(1, 1, QColor(0, 0, 0, 60)), (0, 0, QColor(0, 120, 255))]:
                painter.setPen(Qt.NoPen)
                painter.setBrush(color)
                painter.drawRoundedRect(4, y - 3 + dy, max(0, self.width() - 8), 6, 3, 3)
            painter.end()

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
