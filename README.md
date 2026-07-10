# 日历倒计时 (Calendar Countdown)

轻量化桌面日历倒计时工具，支持公历/农历切换、自定义倒计时事件、实时剩余时间展示。
（ai帮忙做的）

## 功能

- 🕐 实时时钟（HH:MM:SS 秒级刷新）
- 📅 月历视图（公历/农历切换、月份切换、今日高亮）
- ⏱️ 自定义倒计时事件（名称、日期、时间、备注）
- 🏷️ 事件状态标签（正常/即将到期 橙色/已过期 红色）
- 📌 事件置顶、排序、分类
- 📍 窗口置顶、无边框极简设计

## 开发环境

- Python >= 3.11
- PySide6 >= 6.6
- lunardate >= 0.2
- platformdirs >= 4.0

## 快速开始

```bash
# 创建虚拟环境
python -m venv .venv

# 激活 (Windows)
.venv\Scripts\activate

# 安装依赖
pip install -e .

# 运行
python main.py
```

## 项目结构

```
calendar-countdown/
├── main.py                 # 入口
├── pyproject.toml          # 项目配置
├── app/
│   ├── config.py           # 全局常量
│   ├── data/
│   │   ├── models.py       # 数据模型 (Event, EventStatus)
│   │   └── event_store.py  # JSON 持久化
│   ├── logic/
│   │   ├── countdown.py    # 倒计时计算
│   │   ├── lunar_converter.py  # 农历转换
│   │   └── event_sorter.py # 事件排序
│   └── ui/
│       ├── main_window.py  # 主窗口
│       ├── title_bar.py    # 标题栏
│       ├── clock_widget.py # 实时时钟
│       ├── calendar_widget.py  # 月历
│       ├── event_card.py   # 事件卡片
│       ├── event_list.py   # 事件列表
│       ├── event_dialog.py # 新增/编辑弹窗
│       ├── left_panel.py   # 左侧面板
│       ├── right_panel.py  # 右侧面板
│       ├── bottom_bar.py   # 底部栏
│       └── styles.py       # QSS 样式
└── tests/
```

## 数据存储

事件数据存储在：
- Windows: `%LOCALAPPDATA%\CalendarCountdown\events.json`
- macOS: `~/Library/Application Support/CalendarCountdown/events.json`
