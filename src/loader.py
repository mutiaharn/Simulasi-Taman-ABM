import pandas as pd
import os

class DataLoader:
    def __init__(self, data_dir="data"):
        """
        Inisialisasi DataLoader dengan pencarian path otomatis.
        Ini memastikan Python tidak 'tersesat' saat mencari folder data.
        """
        # 1. Cari tahu lokasi file loader.py ini
        current_script_path = os.path.abspath(__file__)
        src_directory = os.path.dirname(current_script_path)
        
        # 2. Mundur satu langkah ke folder project utama (keluar dari src/)
        project_root = os.path.dirname(src_directory)
        
        # 3. Gabungkan dengan nama folder data
        self.data_path = os.path.join(project_root, data_dir)
        
        # Debugging: Konfirmasi lokasi data
        print(f"[DEBUG] DataLoader mencari data di: {self.data_path}")

    def _read_csv(self, filename):
        """Helper function untuk membaca CSV dengan error handling yang jelas."""
        full_path = os.path.join(self.data_path, filename)
        
        if not os.path.exists(full_path):
             print(f"\n❌ ERROR FATAL: File tidak ditemukan!")
             print(f"   Dicari di: {full_path}")
             raise FileNotFoundError(f"File '{filename}' tidak ada. Cek nama file/folder.")
             
        return pd.read_csv(full_path)

    def load_network_data(self):
        """
        Mengambil data nodes (titik) dan edges (jalur) untuk navigasi.
        Output:
            - nodes_dict: {'N001': {'x_m': 73.2, 'y_m': 92.3}, ...}
            - edges_list: [('N001', 'N002', {'length': 15.5}), ...]
        """
        nodes_df = self._read_csv("path_nodes.csv")
        edges_df = self._read_csv("path_edges.csv")
        
        # Konversi Nodes ke Dictionary
        # Kita pakai kolom x_m dan y_m (meter) untuk koordinat simulasi
        nodes_dict = nodes_df.set_index('node_id')[['x_m', 'y_m']].to_dict('index')
        
        # Konversi Edges ke List of Tuples yang disukai NetworkX
        edges_list = []
        for _, row in edges_df.iterrows():
            attr = {
                'length': row['length_m'], 
                'edge_id': row['edge_id'],
                'edge_type': row['edge_type']
            }
            edges_list.append((row['from_node'], row['to_node'], attr))
            
        return nodes_dict, edges_list

    def load_zones(self):
        """
        Mengambil data zona fisik dan menggabungkannya dengan info kapasitas.
        Output: List of dictionaries (records).
        """
        zone_config = self._read_csv("zone_config.csv")
        park_facilities = self._read_csv("park_facilities.csv")
        
        # Gabungkan (Left Join) info lokasi zona dengan kapasitasnya
        merged_zones = pd.merge(
            zone_config, 
            park_facilities[['zone_id', 'total_capacity', 'facility_type']], 
            on='zone_id', 
            how='left'
        )
        
        # Isi NaN capacity dengan 0 (untuk zona tanpa fasilitas spesifik, misal gate)
        merged_zones['total_capacity'] = merged_zones['total_capacity'].fillna(0)
        
        return merged_zones.to_dict('records')

    def load_arrival_profile(self):
        """Mengambil jadwal kedatangan pengunjung."""
        return self._read_csv("arrival_profile_weekend_counts.csv")

    def load_env_schedule(self):
        """Mengambil jadwal cuaca (panas, hujan, cahaya)."""
        return self._read_csv("env_schedule_weekend.csv")

    def load_profiles(self):
        """Mengambil data 1000 profil responden untuk dijadikan template agen."""
        return self._read_csv("survey_preferences_1000.csv")

    def load_activity_rules(self):
        """Mengambil aturan aktivitas (durasi, kebutuhan energi, dll)."""
        return self._read_csv("activity_usage_profile.csv")