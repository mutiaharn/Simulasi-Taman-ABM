import mesa
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
import networkx as nx
import random # <-- Tambahan import
from .loader import DataLoader
from .agent import ParkAgent # <-- Import agen yang baru kita buat

class ParkModel(mesa.Model):
    """
    Model utama simulasi taman (Mesa 3.3.1 Compatible).
    """
    def __init__(self, data_dir="data"):
        super().__init__()
        
        # 1. Load Data
        self.loader = DataLoader(data_dir)
        self.nodes_data, self.edges_data = self.loader.load_network_data()
        self.zones_data = self.loader.load_zones()
        self.schedule_data = self.loader.load_arrival_profile()
        
        # 2. Setup Lingkungan (Graph)
        self.G = nx.Graph()
        for node_id, attr in self.nodes_data.items():
            self.G.add_node(node_id, pos=(attr['x_m'], attr['y_m']))
        self.G.add_edges_from(self.edges_data)
        
        self.grid = NetworkGrid(self.G) 
        
        # 3. Tracking Waktu
        self.current_time_slot_index = 0
        self.time_slots = self.schedule_data['time_slot'].tolist()
        
        self.datacollector = DataCollector(
            model_reporters={"Agent Count": lambda m: len(m.agents)}
        )
        
        # --- SPAWN AGEN TEST (TAHAP 2) ---
        # Kita ambil 1 node acak sebagai start, dan 1 node acak sebagai tujuan
        all_nodes = list(self.G.nodes)
        
        # Coba spawn 1 agen
        start_node = all_nodes[0] # Ambil node pertama di daftar
        target_node = all_nodes[-1] # Ambil node terakhir di daftar
        
        agent_id = "Agent_001"
        agent = ParkAgent(agent_id, self, start_node, target_node)
        
        # Masukkan ke Grid
        self.grid.place_agent(agent, start_node)
        
        # Masukkan ke Scheduler (Mesa 3.0 otomatis track via self.agents, tapi kita add manual biar aman)
        self.agents.add(agent)
        
        print(f"👻 Agen Percobaan dibuat! Posisi: {start_node} -> Tujuan: {target_node}")
        # ---------------------------------

    def step(self):
        current_time = self.time_slots[self.current_time_slot_index % len(self.time_slots)]
        
        # Gerakkan Agen
        self.agents.shuffle_do("step")
        
        self.datacollector.collect(self)
        
        print(f"Step {self.steps}: Jam {current_time} | Agen: {len(self.agents)} | Posisi Agen: {[a.pos for a in self.agents]}")
        
        self.current_time_slot_index += 1