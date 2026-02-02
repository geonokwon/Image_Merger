"""Main window: image list (drag-drop), merge options, save."""
import os
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QScrollArea,
)

from .image_list_widget import ImageListWidget
from .image_merger import load_images, merge_images, MergeDirection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Merger - 드래그 앤 드롭으로 이미지 합치기")
        self.setMinimumSize(480, 400)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Drop zone / list
        group = QGroupBox("이미지 / PDF 목록 (드래그 앤 드롭 또는 추가)")
        group_layout = QVBoxLayout(group)
        self.image_list = ImageListWidget(self)
        group_layout.addWidget(self.image_list)
        add_btn = QPushButton("파일 추가...")
        add_btn.setObjectName("secondary")
        add_btn.clicked.connect(self._on_add_files)
        group_layout.addWidget(add_btn)
        layout.addWidget(group)

        # Options
        opt_layout = QHBoxLayout()
        opt_layout.addWidget(QLabel("합치기 방향:"))
        self.direction_combo = QComboBox()
        self.direction_combo.addItem("세로 (위→아래)", MergeDirection.VERTICAL)
        self.direction_combo.addItem("가로 (왼쪽→오른쪽)", MergeDirection.HORIZONTAL)
        opt_layout.addWidget(self.direction_combo)
        opt_layout.addWidget(QLabel("간격:"))
        self.spacing_spin = QSpinBox()
        self.spacing_spin.setRange(0, 100)
        self.spacing_spin.setValue(0)
        opt_layout.addWidget(self.spacing_spin)
        opt_layout.addWidget(QLabel("최대 변 (px):"))
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(0, 8000)
        self.max_size_spin.setValue(1200)
        self.max_size_spin.setSpecialValueText("리사이즈 안 함")
        self.max_size_spin.setToolTip("각 이미지의 긴 변을 이 값 이하로 줄입니다. 0이면 리사이즈 안 함.")
        opt_layout.addWidget(self.max_size_spin)
        opt_layout.addStretch()
        layout.addLayout(opt_layout)

        # 여백: 드롭다운이 아래 버튼에 가려지지 않도록
        layout.addSpacing(100)

        # Buttons
        btn_layout = QHBoxLayout()
        merge_btn = QPushButton("이미지 합치기")
        merge_btn.clicked.connect(self._on_merge)
        self.save_btn = QPushButton("저장")
        self.save_btn.clicked.connect(self._on_save)
        self.save_btn.setEnabled(False)
        clear_btn = QPushButton("목록 비우기")
        clear_btn.setObjectName("secondary")
        clear_btn.clicked.connect(self._on_clear)
        btn_layout.addWidget(merge_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self._merged_image = None

    def _on_add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "이미지 / PDF 선택",
            "",
            "Images & PDF (*.png *.jpg *.jpeg *.gif *.bmp *.webp *.tiff *.tif *.pdf);;Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp *.tiff *.tif);;PDF (*.pdf);;All (*)",
        )
        if paths:
            self.image_list.add_paths(paths)

    def _on_clear(self):
        self.image_list.clear()
        self._merged_image = None
        self.save_btn.setEnabled(False)

    def _on_merge(self):
        paths = self.image_list.get_paths()
        if not paths:
            QMessageBox.information(self, "알림", "합칠 이미지를 먼저 넣어 주세요.")
            return
        labeled_items = load_images(paths)
        if not labeled_items:
            has_pdf = any(Path(p).suffix.lower() == ".pdf" for p in paths)
            msg = (
                "PDF를 불러오려면 PyMuPDF가 필요합니다.\n"
                "터미널에서: pip install pymupdf"
                if has_pdf
                else "이미지를 불러올 수 없습니다. 파일 형식과 경로를 확인하세요."
            )
            QMessageBox.warning(self, "오류", msg)
            return
        direction = self.direction_combo.currentData()
        spacing = self.spacing_spin.value()
        max_image_size = self.max_size_spin.value()
        try:
            self._merged_image = merge_images(
                labeled_items, direction=direction, spacing=spacing, max_image_size=max_image_size
            )
            self.save_btn.setEnabled(True)
            QMessageBox.information(
                self, "완료", f"블록 {len(labeled_items)}개를 합쳤습니다. '저장'으로 저장하세요."
            )
        except Exception as e:
            QMessageBox.critical(self, "오류", str(e))

    def _on_save(self):
        if self._merged_image is None:
            QMessageBox.information(self, "알림", "먼저 '이미지 합치기'를 실행하세요.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "합친 이미지 저장",
            os.path.expanduser("~/merged_image.png"),
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;All (*)",
        )
        if path:
            try:
                if path.lower().endswith((".jpg", ".jpeg")):
                    self._merged_image.convert("RGB").save(path, "JPEG", quality=95)
                else:
                    if not path.lower().endswith(".png"):
                        path += ".png"
                    self._merged_image.save(path)
                QMessageBox.information(self, "저장 완료", f"저장했습니다:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "저장 오류", str(e))
