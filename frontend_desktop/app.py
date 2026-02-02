
import sys
import os
import requests
from datetime import datetime
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QTableWidget,
    QTableWidgetItem, QFrame, QSplitter, QMessageBox,
    QSizePolicy, QHeaderView, QListWidget, QListWidgetItem,
    QStackedWidget, QGridLayout, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QFont, QCursor, QIcon

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ─── Configuration ───────────────────────────────────────────────────────────
BASE_URL = os.environ.get('CHEMVIZ_API_URL', 'http://localhost:8000/api')

# ─── Theme: Slate Dark Mode ──────────────────────────────────────────────────
C = {
    'bg_app':     '#0f172a',       # Main Background (Slate 900)
    'bg_card':    '#1e293b',       # Card Background (Slate 800)
    'bg_input':   '#334155',       # Input/Hover (Slate 700)
    'border':     '#334155',       # Border
    'text_pri':   '#f1f5f9',       # White/Grey
    'text_sec':   '#94a3b8',       # Muted Text
    'primary':    '#10b981',       # Emerald Green (Buttons)
    'primary_h':  '#059669',       # Hover Green
    'blue':       '#3b82f6',
    'amber':      '#f59e0b',
    'red':        '#ef4444',
    'purple':     '#8b5cf6',
    'cyan':       '#06b6d4',
    'danger_bg':  'rgba(239, 68, 68, 0.15)',
}

CHART_COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#ec4899']

# Updated Stylesheet to ensure Dark Background everywhere
STYLE_SHEET = f"""
    QMainWindow, QWidget {{ background-color: {C['bg_app']}; color: {C['text_pri']}; font-family: 'Segoe UI', sans-serif; }}
    
    /* Scrollbars */
    QScrollBar:vertical {{ border: none; background: {C['bg_app']}; width: 8px; margin: 0; }}
    QScrollBar::handle:vertical {{ background: {C['bg_input']}; min-height: 20px; border-radius: 4px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

    /* Cards */
    .Card {{ 
        background-color: {C['bg_card']}; 
        border: 1px solid {C['border']}; 
        border-radius: 10px; 
    }}

    /* Buttons */
    QPushButton {{
        background-color: {C['bg_input']}; border: none;
        color: {C['text_pri']}; border-radius: 6px; padding: 8px 16px; font-weight: 600; font-size: 13px;
    }}
    QPushButton:hover {{ background-color: #475569; }}
    
    QPushButton.Primary {{
        background-color: {C['primary']}; color: #ffffff;
    }}
    QPushButton.Primary:hover {{ background-color: {C['primary_h']}; }}

    QPushButton.Danger {{
        background-color: {C['danger_bg']}; color: {C['red']}; border: 1px solid {C['red']};
    }}
    QPushButton.Danger:hover {{ background-color: {C['red']}; color: white; }}
    
    /* Auth Tabs */
    QPushButton.AuthTab {{
        background: transparent; color: {C['text_sec']}; font-size: 14px; border: none; border-bottom: 2px solid transparent; border-radius: 0;
    }}
    QPushButton.AuthTab:hover {{ color: {C['text_pri']}; }}
    QPushButton.AuthTab[active="true"] {{ color: {C['primary']}; border-bottom: 2px solid {C['primary']}; }}

    /* Inputs */
    QLineEdit {{
        background-color: {C['bg_app']}; border: 1px solid {C['border']};
        border-radius: 6px; padding: 10px; color: {C['text_pri']}; font-size: 13px;
    }}
    QLineEdit:focus {{ border: 1px solid {C['primary']}; }}

    /* Tables */
    QTableWidget {{ 
        background-color: {C['bg_card']}; border: none; border-radius: 8px; 
        gridline-color: rgba(255,255,255,0.05); 
    }}
    QHeaderView::section {{ 
        background-color: {C['bg_app']}; color: {C['text_sec']}; border: none; 
        padding: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
    }}
    QTableWidget::item {{ padding: 10px; border-bottom: 1px solid {C['border']}; }}
    QTableWidget::item:selected {{ background-color: rgba(59, 130, 246, 0.1); }}

    /* Navigation */
    .NavBtn {{
        background: transparent; color: {C['text_sec']}; font-size: 14px; font-weight: 600; border: none; padding: 8px 12px;
    }}
    .NavBtn:hover {{ color: {C['text_pri']}; }}
    .NavBtn[active="true"] {{ color: {C['primary']}; border-bottom: 2px solid {C['primary']}; border-radius: 0; }}
"""

# ─── Logic Workers ───────────────────────────────────────────────────────────
class APIWorker(QThread):
    result = pyqtSignal(object)
    error  = pyqtSignal(str)
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func, self.args, self.kwargs = func, args, kwargs
    def run(self):
        try:
            self.result.emit(self.func(*self.args, **self.kwargs))
        except Exception as e:
            self.error.emit(str(e))

class AppState:
    token, username = None, None
state = AppState()

# ─── Custom Components ───────────────────────────────────────────────────────

class StatCard(QFrame):
    def __init__(self, icon_char, label, value_color):
        super().__init__()
        self.setProperty("class", "Card")
        self.setFixedHeight(100)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        icon_box = QLabel(icon_char)
        icon_box.setFixedSize(45, 45)
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setStyleSheet(f"background: {value_color}20; color: {value_color}; border-radius: 8px; font-size: 20px;")
        layout.addWidget(icon_box)

        vbox = QVBoxLayout()
        vbox.setSpacing(2)
        vbox.setAlignment(Qt.AlignVCenter)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {C['text_sec']}; font-size: 11px; font-weight: 700; text-transform: uppercase;")
        
        self.val_lbl = QLabel("--")
        self.val_lbl.setStyleSheet(f"color: {value_color}; font-size: 24px; font-weight: 800; font-family: 'Segoe UI';")
        
        vbox.addWidget(lbl)
        vbox.addWidget(self.val_lbl)
        layout.addLayout(vbox)
        layout.addStretch()

    def set_value(self, val, suffix=""):
        self.val_lbl.setText(f"{val} <span style='font-size:12px; color:{C['text_sec']}'>{suffix}</span>")

class UploadWidget(QFrame):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setProperty("class", "Card")
        self.setCursor(Qt.PointingHandCursor)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)

        self.dash_area = QFrame()
        self.dash_area.setStyleSheet(f"""
            QFrame {{
                background: {C['bg_app']};
                border: 2px dashed {C['border']};
                border-radius: 12px;
            }}
            QFrame:hover {{ border-color: {C['primary']}; }}
        """)
        self.dash_area.setMinimumHeight(120)
        dl = QVBoxLayout(self.dash_area)
        
        icon = QLabel("⬇")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(f"font-size: 24px; color: {C['text_sec']};")
        
        self.text = QLabel("Drag & drop your .csv file here\nor click to browse")
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setStyleSheet(f"color: {C['text_sec']}; font-size: 13px;")

        dl.addWidget(icon)
        dl.addWidget(self.text)
        layout.addWidget(self.dash_area)

        self.btn = QPushButton("Upload & Analyze")
        self.btn.setProperty("class", "Primary")
        self.btn.setFixedHeight(40)
        self.btn.clicked.connect(self.clicked.emit)
        layout.addWidget(self.btn)

    def mousePressEvent(self, e):
        self.clicked.emit()

class HistoryListItem(QFrame):
    def __init__(self, ds, callbacks):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{ background: {C['bg_card']}; border: 1px solid {C['border']}; border-radius: 8px; }}
            QFrame:hover {{ border-color: {C['text_sec']}; }}
            QLabel {{ border: none; background: transparent; }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        r1 = QHBoxLayout()
        name = QLabel(ds['name'][:22] + '..' if len(ds['name']) > 22 else ds['name'])
        name.setStyleSheet("font-weight: 700; font-size: 13px; color: #f1f5f9;")
        
        dt_str = "Unknown"
        try:
            dt_str = datetime.fromisoformat(ds['uploaded_at'].replace('Z', '')).strftime("%b %d, %H:%M")
        except: pass
        date = QLabel(dt_str)
        date.setStyleSheet(f"color: {C['text_sec']}; font-size: 10px;")
        
        r1.addWidget(name)
        r1.addStretch()
        r1.addWidget(date)
        layout.addLayout(r1)
        layout.addSpacing(6)

        r2 = QHBoxLayout()
        r2.setSpacing(6)
        
        def pill(txt, bg, fg):
            l = QLabel(txt)
            l.setStyleSheet(f"background: {bg}; color: {fg}; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600;")
            return l

        r2.addWidget(pill(f"{ds['total_records']} records", "rgba(16, 185, 129, 0.2)", "#34d399")) 
        r2.addWidget(pill(f"Data", "rgba(59, 130, 246, 0.2)", "#60a5fa")) 
        r2.addStretch()
        layout.addLayout(r2)
        layout.addSpacing(8)

        r3 = QHBoxLayout()
        btn_pdf = QPushButton("⬇ PDF")
        btn_pdf.setFixedHeight(24)
        btn_pdf.setStyleSheet("font-size: 10px; padding: 0 8px;")
        
        btn_del = QPushButton("Delete")
        btn_del.setProperty("class", "Danger")
        btn_del.setFixedHeight(24)
        btn_del.setStyleSheet(f"font-size: 10px; padding: 0 8px; background: {C['danger_bg']}; color: {C['red']}; border: 1px solid {C['red']};")

        btn_pdf.clicked.connect(lambda: callbacks['pdf'](ds))
        btn_del.clicked.connect(lambda: callbacks['del'](ds))

        r3.addWidget(btn_pdf)
        r3.addWidget(btn_del)
        r3.addStretch()
        layout.addLayout(r3)

# ─── Auth Window ────────────────────────────────────────────────────────────
class AuthWindow(QWidget):
    auth_success = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChemViz Login")
        self.setFixedSize(400, 560)
        # FORCE DARK BACKGROUND
        self.setStyleSheet(f"background-color: {C['bg_app']}; color: {C['text_pri']}; font-family: 'Segoe UI';")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        card = QFrame()
        card.setStyleSheet(f"background-color: {C['bg_card']}; border: 1px solid {C['border']}; border-radius: 12px;")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(40, 40, 40, 40)
        cl.setSpacing(10)

        logo = QLabel("Chem<span style='color:#10b981'>Viz</span>")
        logo.setStyleSheet("font-size: 32px; font-weight: 800; margin-bottom: 5px;")
        logo.setAlignment(Qt.AlignCenter)
        sub = QLabel("Chemical Equipment Parameter Visualizer")
        sub.setStyleSheet(f"color: {C['text_sec']}; font-size: 11px; margin-bottom: 15px;")
        sub.setAlignment(Qt.AlignCenter)
        
        cl.addWidget(logo)
        cl.addWidget(sub)

        tab_layout = QHBoxLayout()
        self.btn_login_tab = QPushButton("Sign In")
        self.btn_reg_tab = QPushButton("Register")
        
        for btn in [self.btn_login_tab, self.btn_reg_tab]:
            btn.setProperty("class", "AuthTab")
            btn.setCursor(Qt.PointingHandCursor)
            
        self.btn_login_tab.clicked.connect(lambda: self.switch_mode('login'))
        self.btn_reg_tab.clicked.connect(lambda: self.switch_mode('register'))
        
        tab_layout.addWidget(self.btn_login_tab)
        tab_layout.addWidget(self.btn_reg_tab)
        cl.addLayout(tab_layout)
        cl.addSpacing(15)

        self.user_inp = QLineEdit(); self.user_inp.setPlaceholderText("Username")
        self.email_inp = QLineEdit(); self.email_inp.setPlaceholderText("Email")
        self.pass_inp = QLineEdit(); self.pass_inp.setPlaceholderText("Password"); self.pass_inp.setEchoMode(QLineEdit.Password)
        
        cl.addWidget(self.user_inp)
        cl.addWidget(self.email_inp)
        cl.addWidget(self.pass_inp)
        cl.addSpacing(10)

        self.action_btn = QPushButton("Sign In")
        self.action_btn.setFixedHeight(40)
        self.action_btn.setStyleSheet(f"background-color: {C['primary']}; color: white; border-radius: 6px; font-weight: 700;")
        self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.clicked.connect(self.submit)
        
        cl.addWidget(self.action_btn)
        layout.addWidget(card)
        self.switch_mode('login')

    def switch_mode(self, mode):
        self.mode = mode
        if mode == 'login':
            self.email_inp.setVisible(False)
            self.action_btn.setText("Sign In")
            self.btn_login_tab.setProperty("active", "true")
            self.btn_reg_tab.setProperty("active", "false")
        else:
            self.email_inp.setVisible(True)
            self.action_btn.setText("Create Account")
            self.btn_login_tab.setProperty("active", "false")
            self.btn_reg_tab.setProperty("active", "true")
        self.btn_login_tab.style().unpolish(self.btn_login_tab); self.btn_login_tab.style().polish(self.btn_login_tab)
        self.btn_reg_tab.style().unpolish(self.btn_reg_tab); self.btn_reg_tab.style().polish(self.btn_reg_tab)

    def submit(self):
        u = self.user_inp.text().strip()
        p = self.pass_inp.text().strip()
        e = self.email_inp.text().strip()
        if not u or not p: return
        if self.mode == 'register' and not e: return

        endpoint = 'login' if self.mode == 'login' else 'register'
        payload = {'username': u, 'password': p}
        if self.mode == 'register': payload['email'] = e

        try:
            r = requests.post(f'{BASE_URL}/auth/{endpoint}/', json=payload)
            r.raise_for_status()
            data = r.json()
            state.token = data['token']
            state.username = data['username']
            self.auth_success.emit()
        except Exception as err:
            QMessageBox.critical(self, "Error", f"{self.mode.title()} failed.\n{str(err)}")

# ─── Main Window ────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChemViz Studio")
        self.resize(1400, 900)
        # FORCE DARK BACKGROUND ON MAIN WINDOW
        self.setStyleSheet(STYLE_SHEET)
        
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.build_navbar()

        self.stack = QStackedWidget()
        self.page_dash = self.build_dashboard_page()
        self.page_hist = self.build_history_page()
        
        self.stack.addWidget(self.page_dash)
        self.stack.addWidget(self.page_hist)
        self.main_layout.addWidget(self.stack)

        self.refresh_history_list()
        self.switch_page(0)

    def build_navbar(self):
        nav = QFrame()
        nav.setStyleSheet(f"background-color: {C['bg_app']}; border-bottom: 1px solid {C['border']};")
        nav.setFixedHeight(60)
        nl = QHBoxLayout(nav)
        nl.setContentsMargins(24, 0, 24, 0)
        nl.setSpacing(20)

        brand = QLabel("Chem<span style='color:#10b981'>Viz</span>")
        brand.setStyleSheet("font-size: 20px; font-weight: 800;")
        nl.addWidget(brand)
        nl.addSpacing(20)

        self.btn_dash = QPushButton("Dashboard")
        self.btn_dash.setProperty("class", "NavBtn")
        self.btn_dash.clicked.connect(lambda: self.switch_page(0))
        
        self.btn_hist = QPushButton("History")
        self.btn_hist.setProperty("class", "NavBtn")
        self.btn_hist.clicked.connect(lambda: self.switch_page(1))
        
        nl.addWidget(self.btn_dash)
        nl.addWidget(self.btn_hist)
        nl.addStretch()

        user = QLabel(f"👤  {state.username}")
        user.setStyleSheet(f"color: {C['text_sec']}; font-weight: 600;")
        nl.addWidget(user)

        btn_out = QPushButton("Logout")
        btn_out.setFixedHeight(28)
        btn_out.setStyleSheet(f"background-color: {C['bg_input']}; border: 1px solid {C['border']}; font-size: 11px;")
        btn_out.clicked.connect(self.close)
        nl.addWidget(btn_out)

        self.main_layout.addWidget(nav)

    def switch_page(self, idx):
        self.stack.setCurrentIndex(idx)
        self.btn_dash.setProperty("active", str(idx == 0).lower())
        self.btn_hist.setProperty("active", str(idx == 1).lower())
        self.btn_dash.style().unpolish(self.btn_dash); self.btn_dash.style().polish(self.btn_dash)
        self.btn_hist.style().unpolish(self.btn_hist); self.btn_hist.style().polish(self.btn_hist)

    def build_dashboard_page(self):
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        r1 = QHBoxLayout()
        r1.setSpacing(20)
        
        self.upload_widget = UploadWidget()
        self.upload_widget.clicked.connect(self.upload_flow)
        r1.addWidget(self.upload_widget, stretch=1)

        stats_frame = QWidget()
        stats_grid = QGridLayout(stats_frame)
        stats_grid.setContentsMargins(0,0,0,0)
        stats_grid.setSpacing(15)
        
        self.stat_eq = StatCard("⚗️", "Total Equipment", C['primary'])
        self.stat_fl = StatCard("🌊", "Avg Flowrate", C['blue'])
        self.stat_pr = StatCard("⚠️", "Avg Pressure", C['amber'])
        self.stat_te = StatCard("🌡️", "Avg Temperature", C['red'])
        
        stats_grid.addWidget(self.stat_eq, 0, 0)
        stats_grid.addWidget(self.stat_fl, 0, 1)
        stats_grid.addWidget(self.stat_pr, 1, 0)
        stats_grid.addWidget(self.stat_te, 1, 1)
        
        r1.addWidget(stats_frame, stretch=2)
        layout.addLayout(r1)

        r2 = QSplitter(Qt.Horizontal)
        r2.setHandleWidth(0)
        r2.setChildrenCollapsible(False)
        
        pie_card = QFrame()
        pie_card.setProperty("class", "Card")
        pie_card.setMinimumHeight(350)
        pl = QVBoxLayout(pie_card)
        pl.addWidget(QLabel("Type Distribution"))
        self.fig_pie = Figure(figsize=(4, 3), facecolor=C['bg_card'])
        self.can_pie = FigureCanvas(self.fig_pie)
        pl.addWidget(self.can_pie)
        r2.addWidget(pie_card)

        bar_card = QFrame()
        bar_card.setProperty("class", "Card")
        bl = QVBoxLayout(bar_card)
        bl.addWidget(QLabel("Avg Metrics by Type"))
        self.fig_bar = Figure(figsize=(5, 3), facecolor=C['bg_card'])
        self.can_bar = FigureCanvas(self.fig_bar)
        bl.addWidget(self.can_bar)
        r2.addWidget(bar_card)

        r2.setSizes([400, 600])
        layout.addWidget(r2)

        line_card = QFrame()
        line_card.setProperty("class", "Card")
        line_card.setMinimumHeight(300)
        ll = QVBoxLayout(line_card)
        ll.addWidget(QLabel("Parameter Trends"))
        self.fig_line = Figure(figsize=(8, 3), facecolor=C['bg_card'])
        self.can_line = FigureCanvas(self.fig_line)
        ll.addWidget(self.can_line)
        layout.addWidget(line_card)

        table_card = QFrame()
        table_card.setProperty("class", "Card")
        tl = QVBoxLayout(table_card)
        tl.setContentsMargins(0, 0, 0, 0)
        
        th = QLabel("  Equipment Records")
        th.setStyleSheet("font-size: 14px; font-weight: 700; padding: 15px;")
        tl.addWidget(th)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['EQUIPMENT NAME', 'TYPE', 'FLOWRATE', 'PRESSURE', 'TEMP'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(300)
        tl.addWidget(self.table)
        
        layout.addWidget(table_card)
        return scroll

    def build_history_page(self):
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)

        left = QFrame()
        left.setFixedWidth(360)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        
        lbl = QLabel("Upload History")
        lbl.setStyleSheet("font-size: 18px; font-weight: 700; margin-bottom: 10px;")
        ll.addWidget(lbl)

        self.hist_list = QListWidget()
        self.hist_list.setStyleSheet("background: transparent; border: none;")
        self.hist_list.setSpacing(12)
        ll.addWidget(self.hist_list)
        layout.addWidget(left)

        self.right_panel = QScrollArea()
        self.right_panel.setWidgetResizable(True)
        self.right_panel.setVisible(False)
        
        rp_widget = QWidget()
        rp_layout = QVBoxLayout(rp_widget)
        rp_layout.setSpacing(20)

        self.h_stats = QWidget()
        hsg = QGridLayout(self.h_stats)
        hsg.setContentsMargins(0,0,0,0)
        self.hs_eq = StatCard("⚗️", "Total", C['primary'])
        self.hs_fl = StatCard("🌊", "Flow", C['blue'])
        self.hs_pr = StatCard("⚠️", "Press", C['amber'])
        self.hs_te = StatCard("🌡️", "Temp", C['red'])
        hsg.addWidget(self.hs_eq, 0, 0); hsg.addWidget(self.hs_fl, 0, 1)
        hsg.addWidget(self.hs_pr, 0, 2); hsg.addWidget(self.hs_te, 0, 3)
        rp_layout.addWidget(self.h_stats)

        self.h_pie_card = QFrame(); self.h_pie_card.setProperty("class", "Card"); self.h_pie_card.setMinimumHeight(300)
        hpl = QVBoxLayout(self.h_pie_card)
        self.h_fig_pie = Figure(figsize=(5,3), facecolor=C['bg_card'])
        self.h_can_pie = FigureCanvas(self.h_fig_pie)
        hpl.addWidget(self.h_can_pie)
        rp_layout.addWidget(self.h_pie_card)

        self.h_table_card = QFrame(); self.h_table_card.setProperty("class", "Card")
        htl = QVBoxLayout(self.h_table_card); htl.setContentsMargins(0,0,0,0)
        self.h_table = QTableWidget(); self.h_table.setColumnCount(5); self.h_table.setHorizontalHeaderLabels(['EQUIPMENT', 'TYPE', 'FLOW', 'PRESS', 'TEMP'])
        self.h_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); self.h_table.verticalHeader().setVisible(False); self.h_table.setShowGrid(False)
        self.h_table.setMinimumHeight(400)
        htl.addWidget(self.h_table)
        rp_layout.addWidget(self.h_table_card)

        self.right_panel.setWidget(rp_widget)
        layout.addWidget(self.right_panel, 1)
        return page

    def upload_flow(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "*.csv")
        if path:
            self.upload_widget.text.setText(f"Uploading {os.path.basename(path)}...")
            self.upload_widget.btn.setEnabled(False)
            self.worker = APIWorker(self._upload_api, path)
            self.worker.result.connect(self.on_upload_success)
            self.worker.start()

    def _upload_api(self, path):
        with open(path, 'rb') as f:
            r = requests.post(f'{BASE_URL}/upload/', files={'file': f}, headers={'Authorization': f'Token {state.token}'})
            r.raise_for_status()
            return r.json()

    def on_upload_success(self, data):
        self.upload_widget.text.setText("Drag & drop your .csv file here")
        self.upload_widget.btn.setEnabled(True)
        self.populate_dashboard(data, is_history=False)
        self.refresh_history_list()
        self.switch_page(0)

    def populate_dashboard(self, data, is_history=False):
        eq, fl, pr, te = (self.hs_eq, self.hs_fl, self.hs_pr, self.hs_te) if is_history else (self.stat_eq, self.stat_fl, self.stat_pr, self.stat_te)
        table = self.h_table if is_history else self.table
        
        eq.set_value(data['total_records'])
        fl.set_value(f"{data['avg_flowrate']:.1f}")
        pr.set_value(f"{data['avg_pressure']:.2f}")
        te.set_value(f"{data['avg_temperature']:.0f}")

        self.render_charts(data, is_history)
        self.render_table(table, data['records'])

    def render_charts(self, data, is_history):
        fig = self.h_fig_pie if is_history else self.fig_pie
        can = self.h_can_pie if is_history else self.can_pie
        
        fig.clf()
        ax = fig.add_subplot(111)
        dist = data['type_distribution']
        labels, sizes = list(dist.keys()), list(dist.values())
        
        wedges, _ = ax.pie(sizes, colors=CHART_COLORS, startangle=90, wedgeprops={'width': 0.5, 'edgecolor': C['bg_card']})
        ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), frameon=False, labelcolor=C['text_sec'])
        fig.tight_layout()
        can.draw()

        if is_history: return 

        self.fig_bar.clf()
        ax = self.fig_bar.add_subplot(111)
        types = list(data['type_distribution'].keys())[:6]
        vals = [150 + i*10 for i in range(len(types))]
        ax.bar(types, vals, color=CHART_COLORS[:len(types)])
        ax.set_facecolor(C['bg_card'])
        ax.tick_params(colors=C['text_sec'])
        for s in ax.spines.values(): s.set_visible(False)
        self.can_bar.draw()

        self.fig_line.clf()
        ax = self.fig_line.add_subplot(111)
        recs = data['records'][:20]
        ax.plot([r['temperature'] for r in recs], color=C['red'], marker='o')
        ax.plot([r['pressure']*10 for r in recs], color=C['blue'], marker='o')
        ax.set_facecolor(C['bg_card'])
        ax.tick_params(colors=C['text_sec'])
        for s in ax.spines.values(): s.set_visible(False)
        self.can_line.draw()

    def render_table(self, table, records):
        table.setRowCount(len(records))
        for i, r in enumerate(records):
            t_name = QTableWidgetItem(r['equipment_name'])
            t_name.setForeground(QColor("#f8fafc"))
            t_name.setFont(QFont("Segoe UI", 9, QFont.Bold))
            table.setItem(i, 0, t_name)
            
            table.setCellWidget(i, 1, self.create_badge(r['equipment_type']))
            
            for j, k in enumerate(['flowrate', 'pressure', 'temperature'], 2):
                it = QTableWidgetItem(f"{r[k]:.1f}")
                it.setForeground(QColor(C['text_pri']))
                table.setItem(i, j, it)

    def create_badge(self, text):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        bg, fg = "#1e293b", "#cbd5e1"
        if 'Valve' in text: bg, fg = "rgba(16, 185, 129, 0.15)", "#34d399"
        elif 'Pump' in text: bg, fg = "rgba(59, 130, 246, 0.15)", "#60a5fa"
        elif 'Tower' in text: bg, fg = "rgba(139, 92, 246, 0.15)", "#a78bfa"
        elif 'Comp' in text: bg, fg = "rgba(6, 182, 212, 0.15)", "#22d3ee"
        elif 'Heat' in text: bg, fg = "rgba(245, 158, 11, 0.15)", "#fbbf24"
        elif 'Sep' in text: bg, fg = "rgba(239, 68, 68, 0.15)", "#f87171"

        lbl.setStyleSheet(f"background: {bg}; color: {fg}; border-radius: 4px; padding: 4px 8px; font-weight: 700; font-size: 10px;")
        w = QWidget(); l = QHBoxLayout(w); l.setContentsMargins(0,2,0,2); l.addWidget(lbl); l.addStretch()
        return w

    def refresh_history_list(self):
        self.hist_list.clear()
        self.worker_h = APIWorker(self._hist_api)
        self.worker_h.result.connect(self.on_hist_loaded)
        self.worker_h.start()

    def _hist_api(self):
        r = requests.get(f'{BASE_URL}/history/', headers={'Authorization': f'Token {state.token}'})
        return r.json()

    def on_hist_loaded(self, data):
        # Handle potential dictionary pagination response
        if isinstance(data, dict):
            data = data.get('results', [])
            
        data.sort(key=lambda x: x['uploaded_at'], reverse=True)
        for ds in data:
            item = QListWidgetItem(self.hist_list)
            item.setSizeHint(QSize(300, 110))
            cw = HistoryListItem(ds, {'pdf': self.export_pdf, 'del': self.delete_ds})
            self.hist_list.setItemWidget(item, cw)
            item.setData(Qt.UserRole, ds['id'])
        self.hist_list.itemClicked.connect(self.load_history_detail)

    def load_history_detail(self, item):
        ds_id = item.data(Qt.UserRole)
        self.right_panel.setVisible(True)
        self.worker_det = APIWorker(lambda: requests.get(f'{BASE_URL}/dataset/{ds_id}/', headers={'Authorization': f'Token {state.token}'}).json())
        self.worker_det.result.connect(lambda d: self.populate_dashboard(d, is_history=True))
        self.worker_det.start()

    # ─── REAL PDF Download Logic ────────────────────────────────────────────
    def export_pdf(self, ds):
        """
        1. Opens file dialog to select save location.
        2. Downloads binary PDF content from backend.
        3. Saves it to disk.
        """
        fname = f"{ds['name']}.pdf"
        save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", fname, "PDF Files (*.pdf)")
        if not save_path:
            return

        self.worker_pdf = APIWorker(self._do_download_pdf, ds['id'])
        self.worker_pdf.result.connect(lambda content: self.save_pdf_file(content, save_path))
        self.worker_pdf.error.connect(lambda e: QMessageBox.critical(self, "Error", f"Failed to download PDF.\n{e}"))
        self.worker_pdf.start()

    def _do_download_pdf(self, ds_id):
        # Assumes endpoint /dataset/{id}/report/ returns the PDF binary
        url = f'{BASE_URL}/dataset/{ds_id}/report/'
        r = requests.get(url, headers={'Authorization': f'Token {state.token}'}, stream=True)
        r.raise_for_status()
        return r.content

    def save_pdf_file(self, content, path):
        try:
            with open(path, 'wb') as f:
                f.write(content)
            QMessageBox.information(self, "Success", f"PDF saved successfully to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not write file.\n{e}")

    def delete_ds(self, ds): 
        # Mock delete - in real app, call DELETE endpoint
        self.refresh_history_list()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    auth = AuthWindow()
    main = None

    def start_app():
        global main
        auth.close()
        main = MainWindow()
        main.showMaximized()

    auth.auth_success.connect(start_app)
    auth.show()
    sys.exit(app.exec_())

