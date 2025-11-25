import mesa
import os

print("=== DIAGNOSA MESA ===")
try:
    print(f"📂 Lokasi Instalasi Mesa: {mesa.__file__}")
except:
    print("📂 Lokasi tidak terdeteksi")

try:
    print(f"ℹ️  Versi Mesa: {mesa.__version__}")
except:
    print("ℹ️  Versi tidak terdeteksi")

print("\n--- Tes Import ---")
# Tes 1: Cara Lama/Standar
try:
    from mesa.time import RandomActivation
    print("✅ (Standard) from mesa.time import RandomActivation -> BERHASIL")
except ImportError:
    print("❌ (Standard) from mesa.time import RandomActivation -> GAGAL")

# Tes 2: Cara Baru (Mesa 3.0+)
try:
    from mesa import RandomActivation
    print("✅ (Direct) from mesa import RandomActivation -> BERHASIL")
except ImportError:
    print("❌ (Direct) from mesa import RandomActivation -> GAGAL")