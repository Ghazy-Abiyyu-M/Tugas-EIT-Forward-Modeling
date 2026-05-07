# ui/main_window.py
import sys, csv
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.patches as patches
import numpy as np
from simulation import run_laplace_simulation

MODERN_DARK_QSS = """
QMainWindow, QWidget { background-color: #181818; color: #cccccc; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
QGroupBox { background-color: #252526; border: 1px solid #2f2f2f; border-radius: 8px; margin-top: 15px; padding: 15px 10px 10px 10px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #ffffff; font-weight: 600; }
QSpinBox, QComboBox { background-color: #333333; border: 1px solid #3e3e42; border-radius: 4px; padding: 4px; color: #ffffff; }
QPushButton#btn_run { background-color: #007acc; color: #ffffff; border: none; border-radius: 6px; padding: 10px; font-weight: bold; }
QPushButton#btn_run:hover { background-color: #0098ff; }
QPushButton { background-color: transparent; border: 1px solid #3e3e42; border-radius: 6px; padding: 6px; color:#ccc; }
QPushButton:hover { background-color: #2a2d2e; color: #fff;}
QTableWidget { background-color: #1e1e1e; alternate-background-color: #252526; border: 1px solid #2f2f2f; border-radius: 8px; gridline-color: transparent; }
QHeaderView::section { background-color: #2d2d30; color: #ffffff; border: none; border-bottom: 2px solid #3e3e42; padding: 6px; font-weight: bold;}
QFrame#info_card { background-color: #252526; border: 1px solid #2f2f2f; border-radius: 8px; padding: 10px; }
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tugas Forward Model - Ghazy Abiyyu Maulana")
        self.setGeometry(50, 50, 1300, 850)
        self.setStyleSheet(MODERN_DARK_QSS)
        self.list_anomali = []
        self.current_sim_data = None
        self.initUI()

    def initUI(self):
        central = QWidget(); self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # --- SIDEBAR (LEFT) ---
        sidebar = QWidget(); sidebar.setFixedWidth(320)
        side_layout = QVBoxLayout(sidebar); side_layout.setAlignment(Qt.AlignTop)
        
        # 1. JUDUL TUGAS DI TENGAH
        header = QLabel("TUGAS FORWARD MODEL")
        header.setAlignment(Qt.AlignCenter) # Membuat teks ke tengah
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #00d2ff; margin-bottom: 5px;")
        side_layout.addWidget(header)

        # Domain Setup
        gp_domain = QGroupBox("Domain & Electrodes")
        ly_domain = QVBoxLayout()
        self.lbl_grid = QLabel("Grid Resolution: 50x50")
        self.slider_grid = QSlider(Qt.Horizontal); self.slider_grid.setRange(10, 100); self.slider_grid.setValue(50)
        self.slider_grid.valueChanged.connect(self.on_grid_changed)
        ly_domain.addWidget(self.lbl_grid); ly_domain.addWidget(self.slider_grid)
        
        ly_domain.addWidget(QLabel("Total Electrodes:"))
        self.spin_elec = QSpinBox(); self.spin_elec.setRange(4, 64); self.spin_elec.setValue(16)
        self.spin_elec.valueChanged.connect(self.update_elec_dropdowns)
        ly_domain.addWidget(self.spin_elec)
        
        inj_ly = QHBoxLayout()
        self.cb_inj1 = QComboBox(); self.cb_inj2 = QComboBox()
        inj_ly.addWidget(QLabel("Inj +:")); inj_ly.addWidget(self.cb_inj1)
        inj_ly.addWidget(QLabel("Inj -:")); inj_ly.addWidget(self.cb_inj2)
        ly_domain.addLayout(inj_ly)
        gp_domain.setLayout(ly_domain); side_layout.addWidget(gp_domain)

        # Anomaly Manager
        gp_anom = QGroupBox("Anomaly Manager (Grid Units)")
        ly_anom = QVBoxLayout()
        
        pos_ly = QGridLayout()
        self.sp_ax = QSpinBox(); self.sp_ay = QSpinBox(); self.sp_as = QSpinBox()
        self.on_grid_changed(50) 
        pos_ly.addWidget(QLabel("Kotak X:"), 0, 0); pos_ly.addWidget(self.sp_ax, 0, 1)
        pos_ly.addWidget(QLabel("Kotak Y:"), 1, 0); pos_ly.addWidget(self.sp_ay, 1, 1)
        pos_ly.addWidget(QLabel("Sisi (px):"), 2, 0); pos_ly.addWidget(self.sp_as, 2, 1)
        ly_anom.addLayout(pos_ly)

        self.cb_mat = QComboBox(); self.cb_mat.addItems(["Isolator", "Konduktor"])
        ly_anom.addWidget(QLabel("Material:")); ly_anom.addWidget(self.cb_mat)

        btn_anom = QHBoxLayout()
        self.btn_add = QPushButton("➕ Tambah"); self.btn_add.clicked.connect(self.add_anomaly)
        self.btn_clear = QPushButton("🗑 Reset"); self.btn_clear.clicked.connect(self.clear_anomalies)
        btn_anom.addWidget(self.btn_add); btn_anom.addWidget(self.btn_clear)
        ly_anom.addLayout(btn_anom)
        
        self.lbl_count = QLabel("Anomali Terpasang: 0"); self.lbl_count.setStyleSheet("color: #4ec9b0; font-weight: bold;")
        ly_anom.addWidget(self.lbl_count)
        gp_anom.setLayout(ly_anom); side_layout.addWidget(gp_anom)

        # Actions
        gp_act = QGroupBox("Actions")
        ly_act = QVBoxLayout()
        self.btn_run = QPushButton("▶ Run Simulation"); self.btn_run.setObjectName("btn_run"); self.btn_run.clicked.connect(self.run_sim)
        self.btn_csv = QPushButton("💾 Export CSV"); self.btn_csv.clicked.connect(self.export_csv); self.btn_csv.setEnabled(False)
        self.btn_img = QPushButton("🖼 Save Image"); self.btn_img.clicked.connect(self.save_img); self.btn_img.setEnabled(False)
        ly_act.addWidget(self.btn_run); ly_act.addWidget(self.btn_csv); ly_act.addWidget(self.btn_img)
        gp_act.setLayout(ly_act); side_layout.addWidget(gp_act)

# 2. IDENTITAS MAHASISWA DI BAWAH ACTIONS
        identitas_frame = QFrame()
        identitas_frame.setObjectName("info_card") # Menggunakan kotak background dari CSS
        identitas_ly = QVBoxLayout(identitas_frame)
        identitas_ly.setContentsMargins(10, 15, 10, 15)
        identitas_ly.setSpacing(6)

        lbl_title = QLabel("TEKNIK TOMOGRAFI")
        lbl_nama = QLabel("👨‍💻 CREATED BY")
        lbl_nim = QLabel("Ghazy Abiyyu Maulana")
        lbl_kelas = QLabel("1104220120")

        # Styling per baris dengan warna berbeda
        lbl_title.setStyleSheet("color: #00d2ff; font-size: 15px; font-weight: bold; letter-spacing: 2px;")
        lbl_nama.setStyleSheet("color: #666666; font-size: 13px; font-weight: bold; letter-spacing: 1px;") # Cyan/Biru
        lbl_nim.setStyleSheet("color: #4ec9b0; font-size: 13px; font-weight: bold;") # Hijau Mint
        lbl_kelas.setStyleSheet("color: #e2c08d; font-size: 13px; font-weight: bold;") # Kuning Pastel

        # Set semua rata tengah dan masukkan ke layout
        for lbl in [lbl_title, lbl_nama, lbl_nim, lbl_kelas]:
            lbl.setAlignment(Qt.AlignCenter)
            identitas_ly.addWidget(lbl)

        # Tambahkan margin atas agar berjarak dari Actions
        container_ly = QVBoxLayout()
        container_ly.setContentsMargins(0, 15, 0, 0)
        container_ly.addWidget(identitas_frame)

        side_layout.addLayout(container_ly)
        side_layout.addStretch() # Mendorong elemen ke atas agar sidebar tetap padat dan rapi

        # --- MAIN AREA (RIGHT) ---
        content = QWidget(); ly_content = QVBoxLayout(content)
        self.fig, self.ax = plt.subplots(figsize=(8, 6)); self.fig.patch.set_facecolor('#181818')
        self.canvas = FigureCanvas(self.fig); ly_content.addWidget(self.canvas, stretch=3)

        # Bottom Info
        btm = QHBoxLayout()
        self.st_pan = QWidget(); st_ly = QVBoxLayout(self.st_pan); st_ly.setContentsMargins(0,0,0,0)
        
        def mk_card(t):
            c = QFrame(); c.setObjectName("info_card"); l = QVBoxLayout(c)
            l.addWidget(QLabel(t)); v = QLabel("-"); v.setStyleSheet("color: #4ec9b0; font-size: 16px; font-weight: bold;")
            l.addWidget(v); return c, v
        
        self.c_status, self.v_status = mk_card("STATUS"); self.c_min, self.v_min = mk_card("MIN (V)"); self.c_max, self.v_max = mk_card("MAX (V)")
        st_ly.addWidget(self.c_status); st_ly.addWidget(self.c_min); st_ly.addWidget(self.c_max)
        
        self.tbl = QTableWidget(0, 3); self.tbl.setHorizontalHeaderLabels(["Node", "Role", "Voltage (V)"])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); self.tbl.setAlternatingRowColors(True)
        self.tbl.setShowGrid(False); self.tbl.verticalHeader().setVisible(False)
        
        btm.addWidget(self.st_pan, 1); btm.addWidget(self.tbl, 2); ly_content.addLayout(btm, 1)

        main_layout.addWidget(sidebar); main_layout.addWidget(content)
        self.update_elec_dropdowns(); self.draw_empty()

    def on_grid_changed(self, v):
        self.lbl_grid.setText(f"Grid Resolution: {v}x{v}")
        self.sp_ax.setRange(0, v-1); self.sp_ay.setRange(0, v-1); self.sp_as.setRange(1, v//2)
        self.sp_ax.setValue(v//2); self.sp_ay.setValue(v//2)

    def update_elec_dropdowns(self):
        n = self.spin_elec.value()
        self.cb_inj1.clear(); self.cb_inj2.clear()
        self.cb_inj1.addItems([f"El {i}" for i in range(n)]); self.cb_inj2.addItems([f"El {i}" for i in range(n)])
        self.cb_inj2.setCurrentIndex(min(8, n-1))

    def add_anomaly(self):
        self.list_anomali.append({'x': self.sp_ax.value(), 'y': self.sp_ay.value(), 's': self.sp_as.value(), 'val': 0.01 if self.cb_mat.currentIndex()==0 else 10.0})
        self.lbl_count.setText(f"Anomali Terpasang: {len(self.list_anomali)}")

    def clear_anomalies(self):
        self.list_anomali.clear(); self.lbl_count.setText("Anomali Terpasang: 0")

    def draw_empty(self):
        self.ax.clear(); self.ax.set_facecolor('#181818')
        self.ax.text(0.5, 0.5, "Klik 'Run Simulation'", color='gray', ha='center', va='center', transform=self.ax.transAxes)
        self.canvas.draw()

    def run_sim(self):
        self.v_status.setText("Computing..."); QApplication.processEvents()
        try:
            res = run_laplace_simulation(self.spin_elec.value(), (self.cb_inj1.currentIndex(), self.cb_inj2.currentIndex()), self.slider_grid.value(), self.list_anomali)
            self.current_sim_data = res
            self.fig.clear(); self.ax = self.fig.add_subplot(111); self.ax.set_facecolor('#181818')
            img = self.ax.imshow(res['V_2d'], cmap='inferno', origin='lower', interpolation='nearest')
            self.fig.colorbar(img, ax=self.ax).set_label('Potential (V)', color='#ccc')
            
            for a in self.list_anomali:
                self.ax.add_patch(patches.Rectangle((a['x']-a['s']/2, a['y']-a['s']/2), a['s'], a['s'], linewidth=2, edgecolor='cyan' if a['val']<1 else 'red', facecolor='none', linestyle='--'))
            
            nodes = res['node_elektroda']; Nx = self.slider_grid.value()
            x_el = [e % Nx for e in nodes]; y_el = [e // Nx for e in nodes]
            self.ax.scatter(x_el, y_el, c='#ccc', s=40, edgecolors='#181818')
            self.ax.scatter([x_el[self.cb_inj1.currentIndex()]], [y_el[self.cb_inj1.currentIndex()]], c='lime', s=100, edgecolors='white')
            self.ax.scatter([x_el[self.cb_inj2.currentIndex()]], [y_el[self.cb_inj2.currentIndex()]], c='red', s=100, edgecolors='white')
            
            self.canvas.draw()
            self.tbl.setRowCount(len(nodes))
            for i, v in enumerate(res['variabel_terukur']):
                self.tbl.setItem(i,0,QTableWidgetItem(f"El {i}")); self.tbl.setItem(i,1,QTableWidgetItem("Inj+" if i==self.cb_inj1.currentIndex() else "Inj-" if i==self.cb_inj2.currentIndex() else "Pasif"))
                it_v = QTableWidgetItem(f"{v:.6f}"); it_v.setTextAlignment(Qt.AlignRight); self.tbl.setItem(i,2,it_v)
            
            self.v_status.setText("Complete ✔"); self.v_min.setText(f"{np.min(res['variabel_terukur']):.4f} V"); self.v_max.setText(f"{np.max(res['variabel_terukur']):.4f} V")
            self.btn_csv.setEnabled(True); self.btn_img.setEnabled(True)
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def export_csv(self):
        p, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if p:
            with open(p, 'w', newline='') as f:
                w = csv.writer(f); w.writerow(["Node", "Role", "Voltage (V)"])
                for r in range(self.tbl.rowCount()): w.writerow([self.tbl.item(r,0).text(), self.tbl.item(r,1).text(), self.tbl.item(r,2).text()])

    def save_img(self):
        p, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png)")
        if p: self.fig.savefig(p, facecolor=self.fig.get_facecolor()); QMessageBox.information(self, "Saved", "Gambar berhasil disimpan!")