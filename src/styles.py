"""Modern app-wide stylesheet: high contrast buttons, clean layout."""

APP_STYLESHEET = """
    /* Window & base */
    QMainWindow, QWidget {
        background-color: #f0f2f5;
    }

    /* Group box: card-like */
    QGroupBox {
        font-weight: 600;
        font-size: 13px;
        color: #1d1d1f;
        border: 1px solid #d1d5db;
        border-radius: 10px;
        margin-top: 12px;
        padding: 16px 14px 14px 14px;
        background-color: #ffffff;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 14px;
        padding: 0 8px;
        background-color: #ffffff;
        color: #1d1d1f;
    }

    /* Primary buttons: visible, high contrast */
    QPushButton {
        font-size: 13px;
        font-weight: 500;
        padding: 10px 18px;
        border-radius: 8px;
        border: 1px solid #0071e3;
        background-color: #0071e3;
        color: #ffffff;
        min-height: 20px;
    }
    QPushButton:hover {
        background-color: #0077ed;
        border-color: #0077ed;
    }
    QPushButton:pressed {
        background-color: #006edb;
        border-color: #006edb;
    }
    QPushButton:disabled {
        background-color: #a1a1aa;
        border-color: #a1a1aa;
        color: #ffffff;
    }

    /* Secondary style for "파일 추가", "목록 비우기" */
    QPushButton#secondary {
        background-color: #ffffff;
        color: #0071e3;
        border: 1px solid #0071e3;
    }
    QPushButton#secondary:hover {
        background-color: #e8f4fd;
    }
    QPushButton#secondary:pressed {
        background-color: #d6ebfa;
    }

    /* ComboBox */
    QComboBox {
        font-size: 13px;
        padding: 8px 12px;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        background-color: #ffffff;
        color: #1d1d1f;
        min-width: 140px;
    }
    QComboBox:hover {
        border-color: #0071e3;
    }
    QComboBox::drop-down {
        border: none;
        background: transparent;
        width: 24px;
    }
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        selection-background-color: #e8f4fd;
        selection-color: #1d1d1f;
    }

    /* SpinBox */
    QSpinBox {
        font-size: 13px;
        padding: 8px 12px;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        background-color: #ffffff;
        color: #1d1d1f;
        min-width: 60px;
    }
    QSpinBox:hover {
        border-color: #0071e3;
    }

    /* Labels */
    QLabel {
        font-size: 13px;
        color: #1d1d1f;
    }

    /* List widget: drop zone */
    QListWidget {
        font-size: 13px;
        background-color: #f9fafb;
        border: 2px dashed #d1d5db;
        border-radius: 8px;
        padding: 8px;
        color: #374151;
    }
    QListWidget::item {
        padding: 8px;
        border-radius: 6px;
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        margin-bottom: 4px;
    }
    QListWidget::item:hover {
        background-color: #f3f4f6;
        border-color: #d1d5db;
    }
    QListWidget::item:selected {
        background-color: #e8f4fd;
        border-color: #0071e3;
        color: #1d1d1f;
    }
"""
