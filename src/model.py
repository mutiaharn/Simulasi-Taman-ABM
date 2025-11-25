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
        self.zones_list = self.loader.load_zones_combined()
        self.arrival_data, self.env_data = self.loader.load_schedules()
        self.agent_profiles = self.loader.load_profiles()
        self.activity_rules = self.loader.load_activity_profile()
        
        # 2. Setup Spasial (Graph)
        self.G = nx.Graph()
        for node_id, attr in self.nodes_data.items():
            self.G.add_node(node_id, pos=(attr['x_m'], attr['y_m']))
        self.G.add_edges_from(self.edges_data)
        self.grid = NetworkGrid(self.G)
        
        # 3. Mapping Zona ke Node
        # Kita butuh tahu setiap zona itu "pintu masuknya" di node mana
        self.zone_map = {} # Key: zone_id, Value: data lengkap + node terdekat
        self.gate_nodes = [] # List khusus node gate
        
        for zone in self.zones_list:
            # Cari node graph terdekat dari pusat zona
            closest_node = self.get_closest_node(zone['x_center_m'], zone['y_center_m'])
            zone['nav_node'] = closest_node
            self.zone_map[zone['zone_id']] = zone
            
            if zone['zone_type'] == 'gate':
                self.gate_nodes.append(closest_node)
        
        self.track_nodes = ["N116", "N117", "N118", "N119", "N120", "N121", "N122", "N123"]

        # 4. State Lingkungan Dinamis
        self.current_time_idx = 0
        self.current_env = self.env_data.iloc[0] # Baris data cuaca saat ini
        self.current_arrival = self.arrival_data.iloc[0]
        self.step_minute_counter = 0 # 1 Step = 1 Menit
        
        self.datacollector = DataCollector(
            model_reporters={
                "Populasi": lambda m: len(m.agents),
                "Hujan": lambda m: 1 if m.current_env['rain_flag'] else 0,
                "Suhu": lambda m: m.current_env['temperature_index']
            }
        )

    def get_closest_node(self, x, y):
        closest = None; min_d = float('inf')
        for n in self.G.nodes(data=True):
            pos = n[1]['pos']
            d = math.sqrt((pos[0]-x)**2 + (pos[1]-y)**2)
            if d < min_d: min_d = d; closest = n[0]
        return closest

    def update_environment(self):
        """Update waktu, cuaca, dan hitung keramaian zona."""
        # Update Jadwal per 10 menit
        if self.step_minute_counter >= 10:
            self.step_minute_counter = 0
            self.current_time_idx = (self.current_time_idx + 1) % len(self.env_data)
            self.current_env = self.env_data.iloc[self.current_time_idx]
            self.current_arrival = self.arrival_data.iloc[self.current_time_idx]
        
        self.step_minute_counter += 1
        
        # Reset hitungan agen di zona (untuk perhitungan kepadatan real-time)
        for z_id in self.zone_map:
            self.zone_map[z_id]['current_agents'] = 0
            
        # Hitung agen ada di zona mana saja
        # (Sederhana: Kita cek agen sedang menuju atau berada di zona mana)
        for agent in self.agents:
            if agent.target_zone_id and agent.state in ['WALKING', 'ACTIVITY']:
                if agent.target_zone_id in self.zone_map:
                    self.zone_map[agent.target_zone_id]['current_agents'] += 1

    def spawn_agents(self):
        """Spawn agen berdasarkan arrival profile."""
        if self.current_env['rain_flag']: return # Gak ada yang datang pas hujan
        
        # Hitung jumlah spawn
        rate = self.current_arrival['avg_arrivals'] / 10.0
        num = int(rate)
        if random.random() < (rate - num): num += 1
        
        for _ in range(num):
            profile = self.agent_profiles.sample(1).iloc[0].to_dict()
            start_node = random.choice(self.gate_nodes)
            # Tentukan aktivitas awal dominan dari jadwal
            dominant_act = self.current_arrival['dominant_activity']
            
            a = ParkAgent(f"A_{self.steps}_{random.randint(1000,9999)}", self, start_node, profile, dominant_act)
            self.grid.place_agent(a, start_node)
            self.agents.add(a)

    def step(self):
        self.update_environment()
        self.spawn_agents()
        self.agents.shuffle_do("step")
        
        # Bersihkan agen selesai
        to_remove = [a for a in self.agents if a.state == 'FINISHED']
        for a in to_remove:
            self.grid.remove_agent(a)
            self.agents.remove(a)
            
        self.datacollector.collect(self)
        
        t = self.current_env['time_slot']
        rain = "HUJAN 🌧️" if self.current_env['rain_flag'] else "CERAH ☀️"
        print(f"Step {self.steps} | {t} | {rain} | Pop: {len(self.agents)}")