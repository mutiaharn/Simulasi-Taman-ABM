from src.model import ParkModel

# Inisialisasi Model
print("Memulai inisialisasi model...")
try:
    park_model = ParkModel(data_dir="data")
    print("✅ Model berhasil dibuat!")
    print(f"   - Jumlah Node (Titik Jalan): {len(park_model.G.nodes)}")
    print(f"   - Jumlah Edge (Jalur): {len(park_model.G.edges)}")
    print(f"   - Jumlah Zona Terdata: {len(park_model.zones_data)}")

    # Coba jalankan 1 step
    print("\nMenjalankan 1 step simulasi...")
    park_model.step()
    print("✅ Step berhasil dijalankan.")

except Exception as e:
    print(f"❌ Terjadi Error: {e}")

    # ... (bagian atas sama)

    # Coba jalankan 10 step (atau sampai agen sampai)
    print("\nMenjalankan simulasi (Looping)...")
    for i in range(10):
        park_model.step()
        
        # Cek apakah agen sudah sampai tujuan
        # (Kita intip list path agen pertama)
        agent = list(park_model.agents)[0]
        if agent.pos == agent.target_node:
            print(f"🎉 HORE! Agen sampai di tujuan {agent.pos} pada langkah ke-{i+1}")
            break

except Exception as e:
    print(f"❌ Terjadi Error: {e}")