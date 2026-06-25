"""Add / Edit event dialog.

Modal QDialog with form fields:
  - Event name (required)
  - Target date (required)
  - Target time (optional, default 23:59:59)
  - Note (optional)
  - Pin toggle
"""
from datetime import date, time, datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDateEdit, QTimeEdit, QTextEdit, QCheckBox, QPushButton,
    QFormLayout, QMessageBox, QWidget, QSizePolicy,
)

from app.config import (
    FONT_FAMILY, FONT_SIZE_TITLE, FONT_SIZE_NORMAL,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_CARD_BG,
    COLOR_TEXT, COLOR_TEXT_SECONDARY, COLOR_BORDER,
    PADDING_LG, PADDING_MD, PADDING_SM, BORDER_RADIUS,
)
from app.data.models import Event


class EventDialog(QDialog):
    """Modal dialog for creating or editing a countdown event.

    Usage:
      dialog = EventDialog(parent)
      if dialog.exec() == QDialog.Accepted:
          event = dialog.get_event()

      # Edit mode:
      dialog = EventDialog(parent, existing_event)
    """

    def __init__(self, parent=None, event: Event | None = None) -> None:
        super().__init__(parent)
        self._edit_mode = event is not None
        self._original_event = event

        self.setWindowTitle("编辑倒计时事件" if self._edit_mode else "新增倒计时事件")
        self.setMinimumWidth(420)
        self.setMaximumWidth(520)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # Disable default title bar close for frameless parent compatibility
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)

        self._setup_ui()

        # Pre-fill if editing
        if event:
            self._populate(event)

        self.setStyleSheet(f"""
            QDialog {{
                background: {COLOR_CARD_BG};
                border: 1px solid {COLOR_BORDER};
                border-radius: {BORDER_RADIUS}px;
            }}
        """)

    # ── Setup ─────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(PADDING_LG, PADDING_LG, PADDING_LG, PADDING_LG)
        root.setSpacing(PADDING_MD)

        # ── Title bar ─────────────────────────────────────────
        title_row = QHBoxLayout()
        title = QLabel("编辑倒计时事件" if self._edit_mode else "新增倒计时事件")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {COLOR_TEXT};
                background: transparent;
            }}
        """)
        title_row.addWidget(title, stretch=1)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-radius: 14px;
                background: transparent;
                font-size: 14px;
                color: {COLOR_TEXT_SECONDARY};
            }}
            QPushButton:hover {{
                background: #F0F0F0;
                color: {COLOR_TEXT};
            }}
        """)
        close_btn.clicked.connect(self.reject)
        title_row.addWidget(close_btn)
        root.addLayout(title_row)

        # ── Form ──────────────────────────────────────────────
        form = QFormLayout()
        form.setSpacing(PADDING_MD)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        field_style = f"""
            QLineEdit {{
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                padding: 8px;
                font-size: {FONT_SIZE_NORMAL}px;
                background: #FAFBFC;
            }}
            QLineEdit:focus {{
                border-color: {COLOR_PRIMARY};
                background: #FFFFFF;
            }}
        """

        # Event name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入事件名称（如：生日、考试、放假）")
        self.name_input.setStyleSheet(field_style)
        form.addRow("事件名称 *", self.name_input)

        # Target date
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(date.today())
        self.date_input.setStyleSheet(field_style)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        form.addRow("目标日期 *", self.date_input)

        # Target time
        self.time_input = QTimeEdit()
        self.time_input.setTime(time(23, 59, 59))
        self.time_input.setDisplayFormat("HH:mm:ss")
        self.time_input.setStyleSheet(field_style)
        form.addRow("目标时间", self.time_input)

        # Note
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("可记录事件详情（选填）")
        self.note_input.setMaximumHeight(80)
        self.note_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                padding: 6px;
                font-size: {FONT_SIZE_NORMAL}px;
                background: #FAFBFC;
            }}
            QTextEdit:focus {{
                border-color: {COLOR_PRIMARY};
                background: #FFFFFF;
            }}
        """)
        form.addRow("备注", self.note_input)

        # Pin toggle
        self.pin_check = QCheckBox("置顶该事件")
        self.pin_check.setStyleSheet(f"""
            QCheckBox {{
                font-size: {FONT_SIZE_NORMAL}px;
                color: {COLOR_TEXT};
                spacing: 8px;
            }}
        """)
        form.addRow("", self.pin_check)

        root.addLayout(form)

        # ── Separator ─────────────────────────────────────────
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {COLOR_BORDER};")
        root.addWidget(sep)

        # ── Buttons ───────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(PADDING_MD)

        cancel_btn = QPushButton("取消")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {COLOR_BORDER};
                border-radius: 4px;
                padding: 8px 24px;
                font-size: {FONT_SIZE_NORMAL}px;
                background: #FFFFFF;
                color: {COLOR_TEXT};
            }}
            QPushButton:hover {{
                background: #F5F5F5;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        btn_row.addStretch()

        save_btn = QPushButton("确认保存")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-size: {FONT_SIZE_NORMAL}px;
                font-weight: bold;
                background: {COLOR_PRIMARY};
                color: #FFFFFF;
            }}
            QPushButton:hover {{
                background: {COLOR_PRIMARY_HOVER};
            }}
        """)
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)

        root.addLayout(btn_row)

    # ── Populate (Edit Mode) ──────────────────────────────────

    def _populate(self, event: Event) -> None:
        self.name_input.setText(event.name)
        self.date_input.setDate(event.target_date)
        if event.target_time:
            self.time_input.setTime(event.target_time)
        else:
            self.time_input.setTime(time(23, 59, 59))
        self.note_input.setPlainText(event.note)
        self.pin_check.setChecked(event.is_pinned)

    # ── Save / Validate ───────────────────────────────────────

    def _on_save(self) -> None:
        """Validate form and accept if valid."""
        name = self.name_input.text().strip()
        if not name:
            self._show_warning("请完善必填信息", "事件名称不能为空。")
            self.name_input.setFocus()
            return

        target_date = self.date_input.date().toPython()
        if not target_date:
            self._show_warning("请完善必填信息", "请选择目标日期。")
            return

        self.accept()

    def _show_warning(self, title: str, message: str) -> None:
        """Show a simple warning message box."""
        QMessageBox.warning(self, title, message)

    # ── Public API ────────────────────────────────────────────

    def get_event(self) -> Event:
        """Build and return an Event from the form data.

        Call this after exec() returns Accepted.
        """
        name = self.name_input.text().strip()
        target_date = self.date_input.date().toPython()
        target_time = self.time_input.time().toPython()
        note = self.note_input.toPlainText().strip()
        is_pinned = self.pin_check.isChecked()

        if self._edit_mode and self._original_event:
            event = self._original_event
            event.name = name
            event.target_date = target_date
            event.target_time = target_time
            event.note = note
            event.is_pinned = is_pinned
            return event

        return Event(
            name=name,
            target_date=target_date,
            target_time=target_time,
            note=note,
            is_pinned=is_pinned,
        )
