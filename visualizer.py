import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
import networkx as nx
import random
import pandas as pd
from src.model import ParkModel

# --- KONFIGURASI VISUALISASI ---
FRAME_INTERVAL = 100   # Kecepatan animasi (ms)
TOTAL_FRAMES = 600     # Durasi animasi

print("🎥 Menyiapkan Visualisasi Design 2.0...")
print("   Memuat Peta, Fasilitas, dan Agen...")

# 1. Inisialisasi Model
model = ParkModel(data_dir="data")

# 2. Setup Canvas
fig, ax = plt.subplots(figsize=(13, 10))
ax.set_title("Simulasi ABM Taman Kota (Design 2.0)")
ax.set_xlabel("X (Meter)")
ax.set_ylabel("Y (Meter)")
ax.set_aspect('equal')

# ==========================================
# LAYER 1: ZONA AREA (Dari model.zones_list)
# ==========================================
zone_colors = {
    'garden': '#98FB98',       # Pale Green
    'playground': '#FFD700',   # Gold
    'fitness_zone': '#87CEEB', # Sky Blue
    'picnic_area': '#FFB6C1',  # Light Pink
    'gazebo': '#CD853F',       # Peru (Coklat Kayu) -> PERBAIKAN DI SINI
    'bench_zone': '#F5DEB3',   # Wheat
    'public_toilet': '#00CED1',# Dark Turquoise
    'fountain_zone': '#1E90FF',# Dodger Blue
    'gate': '#228B22',         # Forest Green
    'track': '#FF6347',        # Tomato
    'plaza': '#D3D3D3'         # Grey
}

# Gambar Zona
for z in model.zones_list:
    z_type = z['zone_type']
    color = zone_colors.get(z_type, '#D3D3D3')
    
    # Tentukan bentuk & ukuran
    marker = 's' if z.get('shape') == 'rect' else 'o'
    size = 300
    
    # Custom size biar proporsional
    if z_type == 'gate': size = 150
    elif z_type in ['playground', 'picnic_area']: size = 600
    elif z_type == 'public_toilet': size = 200
    elif z_type == 'gazebo': size = 400
    
    ax.scatter(z['x_center_m'], z['y_center_m'], 
               c=color, s=size, marker=marker, alpha=0.6, edgecolors='none')

# ==========================================
# LAYER 2: JALUR (Edges)
# ==========================================
pos = nx.get_node_attributes(model.G, 'pos')
nx.draw_networkx_edges(model.G, pos, ax=ax, edge_color='#cccccc', width=1.5, alpha=0.5)

# ==========================================
# LAYER 3: FASILITAS UMUM (Pohon, Lampu, dll)
# ==========================================
gen_facilities = model.loader._read_csv("general_facilities.csv").to_dict('records')

facility_style = {
    'trash_bin': {'c': 'red', 'm': '.', 's': 40},
    'lamp':      {'c': 'orange', 'm': 'o', 's': 30},
    'tree':      {'c': '#006400', 'm': '^', 's': 120}, # Hijau Tua Segitiga
    'bench':     {'c': '#8B4513', 'm': '_', 's': 60}
}

for f in gen_facilities:
    style = facility_style.get(f['facility_type'], {'c':'black', 'm':'x', 's':20})
    ax.scatter(f['x_center_m'], f['y_center_m'], 
               c=style['c'], marker=style['m'], s=style['s'], alpha=0.9, zorder=2)

# ==========================================
# LAYER 4: AGEN (Dinamis)
# ==========================================
agent_scatter = ax.scatter([], [], c='blue', s=20, label="Pengunjung", zorder=5, edgecolors='white', linewidth=0.3)

# Info Box
info_text = ax.text(0.02, 0.98, "", transform=ax.transAxes, fontsize=11,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

# Legenda Custom
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', label='Pengunjung'),
    Line2D([0], [0], marker='^', color='w', markerfacecolor='#006400', label='Pohon'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', label='Lampu'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='#00CED1', label='Toilet'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='#FFD700', label='Playground'),
]
ax.legend(handles=legend_elements, loc='lower right', ncol=2, fontsize=9)

def update(frame):
    model.step()
    
    # Ambil posisi agen untuk plotting
    x_coords = []
    y_coords = []
    colors = []
    
    if len(model.agents) > 0:
        for agent in model.agents:
            if agent.pos:
                try:
                    node_pos = model.G.nodes[agent.pos]['pos']
                    noise_x = random.uniform(-1.5, 1.5)
                    noise_y = random.uniform(-1.5, 1.5)
                    
                    x_coords.append(node_pos[0] + noise_x)
                    y_coords.append(node_pos[1] + noise_y)
                    
                    # WARNA STATUS AGEN
                    if agent.state == "LEAVING":
                        colors.append('red')       # Pulang
                    elif agent.current_activity == 'shelter_seeking':
                        colors.append('purple')    # Cari Berteduh
                    elif agent.state == "DECIDING":
                        colors.append('yellow')    # Mikir
                    else:
                        colors.append('blue')      # Normal
                except:
                    continue
        
        agent_scatter.set_offsets(list(zip(x_coords, y_coords)))
        if colors:
            agent_scatter.set_color(colors)
    else:
        agent_scatter.set_offsets([])

    # Update Text Info
    t = model.current_env['time_slot']
    temp = model.current_env['temperature_index']
    rain = "HUJAN 🌧️" if model.current_env['rain_flag'] else "CERAH ☀️"
    
    info_text.set_text(
        f"Step: {model.steps}\n"
        f"Jam: {t}\n"
        f"Cuaca: {rain} (Panas: {temp})\n"
        f"Populasi: {len(model.agents)} Orang"
    )
    
    return agent_scatter, info_text

ani = FuncAnimation(fig, update, frames=TOTAL_FRAMES, interval=FRAME_INTERVAL, blit=False, repeat=False)
plt.show()