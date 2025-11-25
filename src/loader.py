import pandas as pd
import os

class DataLoader:
    def __init__(self, data_dir="data"):
        current_script_path = os.path.abspath(__file__)
        src_directory = os.path.dirname(current_script_path)
        project_root = os.path.dirname(src_directory)
        self.data_path = os.path.join(project_root, data_dir)
        print(f"[DEBUG] DataLoader path: {self.data_path}")

    def _read_csv(self, filename):
        full_path = os.path.join(self.data_path, filename)
        if not os.path.exists(full_path):
             # Fallback logic untuk nama file yang mungkin beda
             return pd.DataFrame() 
        return pd.read_csv(full_path)

    def load_network_data(self):
        """Memuat Nodes dan Edges untuk navigasi fisik."""
        nodes_df = self._read_csv("path_nodes.csv")
        edges_df = self._read_csv("path_edges.csv")
        
        nodes_dict = nodes_df.set_index('node_id')[['x_m', 'y_m']].to_dict('index')
        
        edges_list = []
        for _, row in edges_df.iterrows():
            attr = {'length': row['length_m'], 'edge_id': row['edge_id']}
            edges_list.append((row['from_node'], row['to_node'], attr))
            
        return nodes_dict, edges_list

    def load_zones_combined(self):
        """
        Menggabungkan zone_config (spasial) dengan park_facilities (kapasitas/atribut).
        Sesuai desain: Zona harus punya kapasitas, amenities_score, dll.
        """
        zone_config = self._read_csv("zone_config.csv")
        park_facilities = self._read_csv("park_facilities.csv")
        
        # 1. Agregasi data fasilitas per zona untuk mendapatkan total kapasitas & amenities score
        # Kita asumsikan amenities_score dihitung dari rata-rata kualitas fasilitas atau random jika tidak ada
        
        # Gabungkan data
        merged = pd.merge(zone_config, park_facilities, on=['zone_id', 'zone_type'], how='left')
        
        # Isi nilai kosong
        merged['zone_max_capacity'] = merged['zone_max_capacity'].fillna(20) # Default kapasitas kecil
        merged['total_capacity'] = merged['total_capacity'].fillna(20)
        
        # Convert ke dictionary dengan zone_id sebagai key
        zones_dict = {}
        for _, row in merged.iterrows():
            z_id = row['zone_id']
            if z_id not in zones_dict:
                zones_dict[z_id] = row.to_dict()
                # Tambahkan field dinamis untuk simulasi
                zones_dict[z_id]['current_agents'] = 0
                zones_dict[z_id]['amenities_score'] = 0.8 # Placeholder score (0-1)
                
                # Tentukan Supported Activities berdasarkan Tipe Zona
                # (Sesuai dokumen Activity Usage Profile)
                z_type = row['zone_type']
                supported = []
                if z_type == 'track': supported = ['running', 'walking', 'cycling']
                elif z_type == 'garden': supported = ['walking', 'relax', 'photo', 'eating', 'reading']
                elif z_type == 'playground': supported = ['playing', 'photo', 'walking']
                elif z_type == 'fitness_zone': supported = ['exercise', 'stretching']
                elif z_type == 'picnic_area': supported = ['eating', 'relax', 'socializing']
                elif z_type == 'gazebo': supported = ['relax', 'reading', 'socializing', 'eating']
                elif z_type == 'bench_zone': supported = ['resting', 'reading', 'eating']
                elif z_type == 'gate': supported = ['leaving'] # Khusus Gate
                
                zones_dict[z_id]['supported_activities'] = supported
            
        return list(zones_dict.values())

    def load_profiles(self):
        return self._read_csv("survey_preferences_1000.csv")

    def load_activity_profile(self):
        """Memuat parameter aktivitas (durasi, energi, penalti)."""
        df = self._read_csv("activity_usage_profile.csv")
        # Convert ke dict biar cepat aksesnya: {activity_name: {data}}
        return df.set_index('activity_name').to_dict('index')

    def load_schedules(self):
        arrival = self._read_csv("arrival_profile_weekend_counts.csv")
        env = self._read_csv("env_schedule_weekend.csv")
        return arrival, env