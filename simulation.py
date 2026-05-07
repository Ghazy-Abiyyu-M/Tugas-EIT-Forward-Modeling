# simulation.py
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

def run_laplace_simulation(jumlah_elektroda, pasangan_injeksi, ukuran_grid, list_anomali=None):
    Nx, Ny = ukuran_grid, ukuran_grid
    N_total = Nx * Ny

    # 1. Menentukan posisi elektroda
    perimeter_nodes = []
    for x in range(Nx): perimeter_nodes.append(x)                          
    for y in range(1, Ny): perimeter_nodes.append(y * Nx + (Nx - 1))       
    for x in range(Nx - 2, -1, -1): perimeter_nodes.append((Ny - 1) * Nx + x) 
    for y in range(Ny - 2, 0, -1): perimeter_nodes.append(y * Nx)          

    step = len(perimeter_nodes) // jumlah_elektroda
    node_elektroda = [perimeter_nodes[i * step] for i in range(jumlah_elektroda)]

    # 2. Distribusi Konduktivitas (Sigma) dengan Multi-Anomali Kotak
    sigma = np.ones(N_total)
    if list_anomali:
        for anom in list_anomali:
            cx, cy = anom['x'], anom['y'] # Pusat kotak (indeks grid)
            s = anom['s']                 # Ukuran sisi (jumlah kotak)
            val = anom['val']
            
            min_x = max(0, int(cx - s/2))
            max_x = min(Nx - 1, int(cx + s/2))
            min_y = max(0, int(cy - s/2))
            max_y = min(Ny - 1, int(cy + s/2))
            
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    sigma[y * Nx + x] = val

    # 3. Matriks Sistem Laplace
    data, row, col = [], [], []
    for i in range(N_total):
        x, y = i % Nx, i // Nx
        sum_C = 0.0
        if x < Nx - 1:
            j = i + 1; C = (sigma[i] + sigma[j]) / 2.0; row.append(i); col.append(j); data.append(C); sum_C += C
        if x > 0:
            j = i - 1; C = (sigma[i] + sigma[j]) / 2.0; row.append(i); col.append(j); data.append(C); sum_C += C
        if y < Ny - 1:
            j = i + Nx; C = (sigma[i] + sigma[j]) / 2.0; row.append(i); col.append(j); data.append(C); sum_C += C
        if y > 0:
            j = i - Nx; C = (sigma[i] + sigma[j]) / 2.0; row.append(i); col.append(j); data.append(C); sum_C += C
        row.append(i); col.append(i); data.append(-sum_C)
        
    A = sp.csr_matrix((data, (row, col)), shape=(N_total, N_total)).tolil()

    # 4. Injeksi Arus & Ground
    b = np.zeros(N_total)
    idx_inj1, idx_inj2 = pasangan_injeksi
    b[node_elektroda[idx_inj1]] = 1.0  
    b[node_elektroda[idx_inj2]] = -1.0 

    ground_node = next(el for el in node_elektroda if el not in [node_elektroda[idx_inj1], node_elektroda[idx_inj2]])
    A[ground_node, :] = 0
    A[ground_node, ground_node] = 1.0
    b[ground_node] = 0.0

    V = spl.spsolve(A.tocsr(), b)
    return {
        "V_2d": V.reshape((Ny, Nx)),
        "node_elektroda": node_elektroda,
        "variabel_terukur": V[node_elektroda],
        "grid_shape": (Nx, Ny),
        "ground_node": ground_node
    }