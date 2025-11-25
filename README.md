# Simulasi-Taman-ABM
Tugas Hands On Mata Kuliah Pemodelan dan Simulasi yang sangat menarik

Simulasi Perilaku Pengunjung Taman Kota (Agent-Based Modeling)

📋 Deskripsi ProjectProject ini adalah simulasi Agent-Based Modeling (ABM) yang dirancang untuk memodelkan dinamika dan perilaku pengunjung di sebuah taman kota. Tujuan utama dari simulasi ini adalah untuk mengevaluasi efektivitas desain ruang, mengidentifikasi titik kepadatan (hotspot), dan memahami bagaimana faktor lingkungan (cuaca, waktu, fasilitas) mempengaruhi kenyamanan pengunjung.
Dibangun menggunakan Python dengan framework Mesa, simulasi ini mengintegrasikan data spasial (GIS-like), data demografis pengunjung, dan profil aktivitas untuk menciptakan lingkungan virtual yang dinamis.

🚀 Fitur Utama
Lingkungan Spasial Eksplisit: Taman dimodelkan menggunakan Graph (Nodes & Edges) yang merepresentasikan jalur pedestrian, zona aktivitas (taman, playground, gate), dan fasilitas fisik.
Agen Cerdas (Heterogen): Setiap agen (pengunjung) memiliki profil unik (usia, preferensi aktivitas, toleransi keramaian, dan ketahanan terhadap panas).
Pengambilan Keputusan Berbasis Filter: Agen tidak bergerak acak, melainkan menggunakan logika 4-tahap: Identifikasi Kebutuhan $\rightarrow$ Filter Kandidat Zona $\rightarrow$ Eliminasi Penalti (Crowd/Heat) $\rightarrow$ Keputusan Akhir.
Dinamika Waktu & Cuaca: Simulasi berjalan mengikuti jadwal dunia nyata (arrival profile). Perubahan cuaca (hujan/panas) secara real-time mempengaruhi perilaku agen (misal: berteduh saat hujan).
Visualisasi Real-Time: Menggunakan Matplotlib untuk memvisualisasikan pergerakan agen, status zona, dan fasilitas secara animasi.🛠️ Teknologi yang DigunakanPython 3.10+Mesa (3.x): Framework inti Agent-Based Modeling.
NetworkX: Untuk manajemen graf spasial dan algoritma pencarian jalur terpendek (Dijkstra).Pandas: Untuk manajemen data input (CSV).Matplotlib: Untuk visualisasi animasi 2D.

📂 Struktur Project
Simulasi Taman/
│
├── data/                         # Folder Dataset (CSV)
│   ├── path_nodes.csv            # Koordinat titik navigasi
│   ├── path_edges.csv            # Jalur penghubung antar titik
│   ├── zone_config.csv           # Konfigurasi zona area (Playground, Garden, dll)
│   ├── park_facilities.csv       # Kapasitas zona
│   ├── general_facilities.csv    # Objek kecil (Lampu, Pohon, Tong Sampah)
│   ├── survey_preferences.csv    # Data profil agen (preferensi)
│   ├── activity_usage.csv        # Aturan durasi aktivitas
│   └── ... (Jadwal cuaca & kedatangan)
│
├── src/                          # Source Code Utama
│   ├── __init__.py
│   ├── agent.py                  # Logika perilaku Agen (Brain)
│   ├── model.py                  # Logika lingkungan & Environment (World)
│   └── loader.py                 # Modul pembacaan data CSV
│
├── run.py                        # Skrip untuk menjalankan simulasi (Headless/Log mode)
├── visualizer.py                 # Skrip untuk menjalankan visualisasi animasi
├── requirements.txt              # Daftar library python
└── README.md                     # Dokumentasi project

🧠 Logika & Algoritma (Under the Hood)
1. Navigasi AgenAgen bergerak di atas NetworkGrid. Rute dari titik A ke titik B dihitung menggunakan algoritma Dijkstra berdasarkan jarak meter (length_m) yang tertera pada data path_edges.csv.
2. Decision Making (Otak Agen)Berbeda dengan model acak sederhana, agen di sini menggunakan pendekatan Filter-Based Decision Making:Activity Selection: Agen memilih aktivitas berdasarkan minat tertinggi (misal: Jogging) atau trigger lingkungan (misal: Hujan $\rightarrow$ Cari Shelter).Candidate Filtering: Sistem mencari zona mana saja yang mendukung aktivitas tersebut.Penalty Check:Crowd Penalty: Jika zona terlalu penuh melebihi toleransi crowd_dislike agen, zona dicoret.Heat Penalty: Jika suhu tinggi dan agen memiliki heat_dislike tinggi, zona terbuka (tanpa peneduh) dicoret.Final Action: Agen berjalan menuju zona terbaik yang lolos seleksi.
3. Logika "Satpol PP" (Jam Tutup)Simulasi memiliki jam operasional. Saat jam tutup tiba (misal 17:00), sistem secara otomatis menginstruksikan seluruh agen yang masih berada di dalam taman untuk membatalkan aktivitas dan mencari rute terdekat menuju Gate keluar.

📊 Data Input
Simulasi ini digerakkan sepenuhnya oleh data (Data-Driven). Anda dapat mengubah layout taman atau perilaku pengunjung hanya dengan mengedit file CSV di folder data/ tanpa perlu mengubah kodingan.

🚧 Status Pengembangan & Rencana Kedepan
Project ini masih dalam tahap pengembangan (Beta). Beberapa hal yang direncanakan untuk update selanjutnya:[ ] Interaksi Antar Agen: Menambahkan logika sosial (misal: agen berinteraksi/mengobrol jika berpapasan).[ ] Antrian Fasilitas: Menambahkan logika antrian (queueing) pada fasilitas dengan kapasitas terbatas (seperti Toilet).[ ] Dashboard Analytics: Membuat dashboard terpisah untuk menampilkan grafik kepadatan dan utilitas zona secara statistik.[ ] Visualisasi 3D: Mengembangkan visualisasi yang lebih imersif.
