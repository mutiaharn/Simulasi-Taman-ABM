from src.model import ParkModel

print("🌳 MEMULAI SIMULASI ABM (DESIGN 2.0) 🌳")
print("   - Evaluasi Perilaku: Filter-Based Decision")
print("   - Kondisi: Hujan, Panas, Keramaian")

try:
    model = ParkModel()
    
    print("\n[TEST RUN] Simulasi 100 Menit...")
    for i in range(100):
        model.step()
        
    print("\n✅ Simulasi Selesai Tanpa Error.")

except Exception as e:
    print(f"\n❌ Error Terdeteksi: {e}")
    import traceback
    traceback.print_exc()