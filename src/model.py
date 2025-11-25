import mesa
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
import networkx as nx
import random
import math
from .loader import DataLoader
from .agent import ParkAgent

class ParkModel(mesa.Model):
    def __init__(self, data_dir="data"):
        super().__init__()
        
        # 1. Load Data
        self.loader = DataLoader(data_dir)
        self.nodes_data, self.edges_data = self.loader.load_network_data()
        self.zones_data = self.loader.load_zones()
        self.schedule_data = self.loader.load_arrival_profile()
        self.profiles_data = self.loader.load_profiles()
        
        # 2. Setup Graph
        self.G = nx.Graph()
        for node_id, attr in self.nodes_data.items():
            self.G.add_node(node_id, pos=(attr['x_m'], attr['y_m']))
        self.G.add_edges_from(self.edges_data)
        
        self.grid = NetworkGrid(self.G)
        
        # Definisi Area Khusus
        self.track_nodes = ["N116", "N117", "N118", "N119", "N120", "N121", "N122", "N123"]
        
        # Setup Gate Nodes
        self.gate_nodes = []
        gate_zones = [z for z in self.zones_data if z['zone_type'] == 'gate']
        if not gate_zones:
            self.gate_nodes = list(self.G.nodes)
        else:
            for gate in gate_zones:
                closest = self.get_closest_node(gate['x_center_m'], gate['y_center_m'])
                if closest: self.gate_nodes.append(closest)
        self.gate_nodes = list(set(self.gate_nodes)) # Hapus duplikat
        
        # 3. Time Management
        # Kita asumsikan 1 Step = 1 Menit simulasi
        self.step_in_slot_counter = 0  # Hitungan menit dalam slot 10-menit
        self.current_schedule_row_idx = 0 
        
        # Simpan row jadwal saat ini biar gak lookup terus
        self.current_schedule_row = self.schedule_data.iloc[0]
        
        self.datacollector = DataCollector(
            model_reporters={"Agent Count": lambda m: len(m.agents)}
        )

    def step(self):
        """Satu langkah simulasi (1 Menit)."""
        
        # --- 1. MANAJEMEN WAKTU & JADWAL ---
        if self.step_in_slot_counter >= 10:
            self.step_in_slot_counter = 0
            self.current_schedule_row_idx += 1
            self.current_schedule_row_idx %= len(self.schedule_data)
            self.current_schedule_row = self.schedule_data.iloc[self.current_schedule_row_idx]
            
        current_time_str = self.current_schedule_row['time_slot']
        
        # Ambil Jam (angka depan) untuk cek jam tutup
        # Format "06:00-06:10" -> ambil "06" -> int(6)
        current_hour = int(current_time_str.split(':')[0])
        
        # --- LOGIKA JAM TUTUP (Satpol PP Mode) ---
        # Misal taman tutup jam 17:00 (5 sore)
        is_closing_time = current_hour >= 17 or current_hour < 5 # Tutup jam 17 sore sampai 5 pagi
        
        num_to_spawn = 0
        agents_evacuated = 0
        
        if not is_closing_time:
            # --- MASIH BUKA: Spawn Normal ---
            total_arrivals_in_slot = self.current_schedule_row['avg_arrivals']
            avg_agents_per_min = total_arrivals_in_slot / 10.0
            
            num_to_spawn = int(avg_agents_per_min)
            if random.random() < (avg_agents_per_min - num_to_spawn):
                num_to_spawn += 1
                
            for _ in range(num_to_spawn):
                self.spawn_agent()
        else:
            # --- SUDAH TUTUP: Usir Semua Orang! ---
            for agent in self.agents:
                if agent.state not in ["LEAVING", "FINISHED"]:
                    agent.go_home()
                    agents_evacuated += 1
            
            if agents_evacuated > 0:
                print(f"📢 PENGUMUMAN: Taman Tutup! Mengusir {agents_evacuated} pengunjung bandel.")

        # --- 3. GERAKKAN AGEN ---
        self.agents.shuffle_do("step")
        
        # --- 4. BERSIHKAN AGEN YG SUDAH PULANG ---
        agents_to_remove = [a for a in self.agents if a.state == "FINISHED"]
        for a in agents_to_remove:
            self.grid.remove_agent(a)
            self.agents.remove(a)
            
        # Data & Logging
        self.datacollector.collect(self)
        self.step_in_slot_counter += 1
        
        status_msg = "TUTUP ⛔" if is_closing_time else "BUKA ✅"
        print(f"Step {self.steps} | {status_msg} | Jam {current_time_str} | Populasi: {len(self.agents)} (+{num_to_spawn}, -{len(agents_to_remove)})")
        
    def spawn_agent(self):
        random_profile = self.profiles_data.sample(1).iloc[0].to_dict()
        start_node = random.choice(self.gate_nodes)
        
        # Unique ID kombinasi step + random biar gak bentrok
        agent_id = f"A_{self.steps}_{random.randint(1000,9999)}"
        agent = ParkAgent(agent_id, self, start_node, random_profile)
        
        self.grid.place_agent(agent, start_node)
        self.agents.add(agent)

    # --- HELPER FUNCTIONS ---
    def find_dest_for_activity(self, activity_name, current_pos_node):
        if activity_name == 'running':
            closest = None; min_d = float('inf')
            for t_node in self.track_nodes:
                try:
                    d = nx.shortest_path_length(self.G, current_pos_node, t_node, weight='length')
                    if d < min_d: min_d = d; closest = t_node
                except: continue
            return closest if closest else "N001"
            
        activity_map = {
            'running': ['track', 'inner_path', 'garden'],
            'walking': ['garden', 'inner_path', 'picnic_area', 'bench_zone'],
            'playing': ['playground', 'garden'],
            'exercise': ['fitness_zone', 'garden'],
            'resting': ['bench_zone', 'gazebo', 'picnic_area']
        }
        target_types = activity_map.get(activity_name, ['garden'])
        compat_zones = [z for z in self.zones_data if z['zone_type'] in target_types]
        if not compat_zones: compat_zones = self.zones_data 
        if not compat_zones: return self.gate_nodes[0]
        
        chosen = random.choice(compat_zones)
        return self.get_closest_node(chosen['x_center_m'], chosen['y_center_m'])

    def get_closest_node(self, tx, ty):
        closest = None; min_d = float('inf')
        for n in self.G.nodes(data=True):
            d = math.sqrt((n[1]['pos'][0]-tx)**2 + (n[1]['pos'][1]-ty)**2)
            if d < min_d: min_d = d; closest = n[0]
        return closest