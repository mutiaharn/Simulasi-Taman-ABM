from src.model import ParkModel

print("🌳 MEMULAI SIMULASI TAMAN CERDAS (Sore -> Malam) 🌳")
park_model = ParkModel(data_dir="data")

# --- CHEAT: Kita percepat waktu ke jam 16:50 ---
# Kita lompat index jadwal ke yang jamnya "16:xx"
# Cari index di data jadwal yang jamnya 16
start_index = 0
for idx, row in park_model.schedule_data.iterrows():
    if row['time_slot'].startswith("16:50"):
        start_index = idx
        break

park_model.current_schedule_row_idx = start_index
park_model.current_schedule_row = park_model.schedule_data.iloc[start_index]
print(f"⏩ Time Travel ke jam: {park_model.current_schedule_row['time_slot']}")

print(f"\nMenjalankan simulasi 20 menit (Transisi Buka -> Tutup)...")

# Jalankan 20 step (10 menit buka, 10 menit tutup)
for i in range(20):
    park_model.step()

print("\n✅ Simulasi Selesai.")