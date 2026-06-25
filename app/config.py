"""Application-wide constants and configuration."""
from pathlib import Path
from platformdirs import user_data_dir

# ── Application ──────────────────────────────────────────────
APP_NAME = "日历倒计时"
APP_NAME_EN = "CalendarCountdown"
VERSION = "0.1.0"

# ── Window ───────────────────────────────────────────────────
DEFAULT_WIDTH = 1100
DEFAULT_HEIGHT = 700
MIN_WIDTH = 800
MIN_HEIGHT = 550
LEFT_RIGHT_RATIO = (4, 6)  # Left panel : Right panel

# ── Colors (PRD: 极简浅蓝主色调, 浅灰/白色辅助, 橙色警示, 红色过期) ─
COLOR_PRIMARY = "#4A90D9"         # 极简浅蓝 — 主色调
COLOR_PRIMARY_HOVER = "#357ABD"   # hover 加深
COLOR_PRIMARY_LIGHT = "#D6EAF8"   # 浅蓝背景
COLOR_BG = "#F5F6FA"             # 全局背景浅灰
COLOR_CARD_BG = "#FFFFFF"        # 卡片白
COLOR_TEXT = "#2C3E50"           # 主文字深灰蓝
COLOR_TEXT_SECONDARY = "#95A5A6" # 次要文字灰色
COLOR_TEXT_DIM = "#BDC3C7"       # 已过期日期淡色
COLOR_WARNING = "#FA8C16"        # 橙色 — 即将到期 (3天内)
COLOR_DANGER = "#F5222D"         # 红色 — 已过期
COLOR_SUCCESS = "#52C41A"        # 绿色 — 正常
COLOR_BORDER = "#E8ECF1"         # 边框
COLOR_TODAY = "#4A90D9"          # 今天高亮色
COLOR_WEEKEND = "#D64545"        # 周末日期红色
COLOR_DISABLED = "#BDC3C7"       # 禁用状态
COLOR_TITLE_BAR = "#FFFFFF"      # 标题栏背景
COLOR_BOTTOM_BAR = "#F5F6FA"     # 底部栏背景

# ── Fonts ────────────────────────────────────────────────────
FONT_FAMILY = '"Microsoft YaHei", "PingFang SC", "Noto Sans SC", "Segoe UI", sans-serif'
FONT_SIZE_CLOCK = 48       # 实时时钟大字号
FONT_SIZE_DATE = 14        # 当前日期信息
FONT_SIZE_TITLE = 14       # 标题栏
FONT_SIZE_NORMAL = 13      # 正文
FONT_SIZE_SMALL = 11       # 辅助文字
FONT_SIZE_LUNAR = 10       # 农历小字
FONT_SIZE_COUNTDOWN = 20   # 倒计时数字
FONT_SIZE_EVENT_NAME = 14  # 事件名称
FONT_SIZE_BADGE = 10       # 状态标签

# ── Spacing ──────────────────────────────────────────────────
PADDING_LG = 20
PADDING_MD = 12
PADDING_SM = 8
CARD_MARGIN = 6
BORDER_RADIUS = 8
TITLE_BAR_HEIGHT = 40
BOTTOM_BAR_HEIGHT = 30

# ── Timing ───────────────────────────────────────────────────
REFRESH_INTERVAL_MS = 1000       # 时钟/倒计时刷新间隔
IMMINENT_DAYS = 3                # PRD: 即将到期 = 3天内
STATUS_RECHECK_INTERVAL_S = 60   # 状态重检间隔（秒）

# ── Data ────────────────────────────────────────────────────
DATA_DIR = Path(user_data_dir(APP_NAME_EN, ensure_exists=True))
DATA_FILE = DATA_DIR / "events.json"

# ── Lunar Calendar ───────────────────────────────────────────
LUNAR_MONTH_NAMES = [
    "正月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "冬月", "腊月"
]
LUNAR_DAY_NAMES = [
    "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
]

# ── Default Event ────────────────────────────────────────────
from datetime import time as _time
DEFAULT_TARGET_TIME = _time(23, 59, 59)
