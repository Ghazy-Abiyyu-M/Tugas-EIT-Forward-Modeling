# Laplace Tomography Simulator (Forward Model) ⚡

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-green.svg)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-orange.svg)
![SciPy](https://img.shields.io/badge/SciPy-Sparse_Solver-lightgrey.svg)

Aplikasi simulasi komputasi numerik berbasis antarmuka grafis (GUI) untuk memodelkan **Forward Problem** pada sistem *Electrical Impedance Tomography* (EIT). Perangkat lunak ini menyelesaikan **Persamaan Laplace** menggunakan **Metode Beda Hingga / Finite Difference Method (FDM)** untuk memvisualisasikan distribusi potensial listrik pada suatu penampang ketika diberikan injeksi arus, serta mendeteksi efek dari objek anomali (isolator/konduktor).

Proyek ini dikembangkan sebagai bagian dari Tugas Mata Kuliah **Teknik Tomografi**.

---

## ✨ Fitur Utama

* **GUI Interaktif (Dark Mode):** Antarmuka profesional bergaya *software engineering tool* yang dibangun dengan PyQt5.
* **Customizable Domain:** Pengguna dapat mengatur resolusi matriks grid (contoh: 50x50, 100x100) dan jumlah elektroda (4 hingga 64 elektroda) secara dinamis.
* **Anomaly Manager:** Fitur untuk menambahkan titik anomali berjenis **Isolator** (hambatan tinggi) atau **Konduktor** (hambatan rendah) ke dalam koordinat FDM secara presisi.
* **Real-time Forward Solver:** Komputasi matematis memecahkan matriks sparse $\nabla \cdot (\sigma \nabla V) = 0$ secara efisien menggunakan `scipy.sparse.linalg`.
* **Discrete Pixel Visualization:** Plotting menggunakan `matplotlib.pyplot.imshow` (interpolasi *nearest*) untuk menunjukkan piksel elemen diskrit metode beda hingga.
* **Data Export:** Fitur untuk menyimpan citra hasil simulasi (`.png`) dan mengekspor tabel data tegangan elektroda ke dalam format CSV (`.csv`) untuk keperluan rekonstruksi *Inverse Problem*.

---

## 📸 Tampilan Aplikasi


![Screenshot Aplikasi](https://github.com/Ghazy-Abiyyu-M/Tugas-EIT-Forward-Modeling/blob/main/simulasi.jpeg)

---

## 📐 Dasar Teori (Governing Equation)

Model maju (*Forward Model*) pada tomografi impedansi listrik didasarkan pada persamaan difusi statis (Persamaan Laplace) untuk media konduktif:

$$\nabla \cdot (\sigma \nabla V) = 0$$

Di mana:
* $\sigma$ = Distribusi konduktivitas medium.
* $V$ = Distribusi potensial listrik dalam medium.

Persamaan diferensial parsial ini didiskritisasi menggunakan **Finite Difference Method (FDM)** menjadi sistem persamaan linear $Ax = b$, di mana matriks $A$ mewakili konduktansi spasial antar grid, $b$ mewakili syarat batas injeksi arus dari elektroda, dan $x$ adalah potensial tegangan yang dicari.

---

## 🚀 Cara Instalasi & Menjalankan Program

### 1. Prasyarat (*Requirements*)
Pastikan Anda telah menginstal Python (disarankan versi 3.8 ke atas) di sistem Anda.

### 2. Instalasi Library
Buka terminal / command prompt, lalu instal pustaka (dependensi) yang dibutuhkan dengan perintah berikut:
```
pip install PyQt5 numpy scipy matplotlib
```
### 3. Clone Repository
```bash
git clone https://github.com/Ghazy-Abiyyu-M/Tugas-EIT-Forward-Modeling
cd Tugas-EIT-Forward-Modeling
```
### 4. Jalankan Aplikasi
```
python main.py
```
## 📂 Struktur Direktori
```
📁 Project Root
│
├── 📄 main.py                # Entry point aplikasi PyQt5
├── 📄 simulation.py          # Engine utama: Komputasi matematis Laplace & FDM
├── 📄 README.md              # Dokumentasi proyek
│
└── 📁 ui/                    # Modul Antarmuka Pengguna (View)
    ├── 📄 __init__.py
    └── 📄 main_window.py     # Logika UI, kontrol interaktif, dan rendering Matplotlib
```
👨‍💻 Identitas Pembuat

Nama: Ghazy Abiyyu Maulana

NIM: 1104220120

Program Studi: S1 Teknik Fisika
