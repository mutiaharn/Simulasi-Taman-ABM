import mesa
import networkx as nx
import random

class ParkAgent(mesa.Agent):
    def __init__(self, unique_id, model, start_node, profile):
        super().__init__(model)
        self.unique_id = unique_id
        self.start_node = start_node
        self.profile = profile
        
        # State: WALKING, ACTIVITY, LEAVING, FINISHED
        self.state = "WALKING" 
        self.path = []
        self.target_node = None
        self.activity_duration = 0
        self.chosen_activity = None
        
        # Otak awal: Tentukan mau ngapain
        self.plan_activity()

    def plan_activity(self):
        # 1. Pilih aktivitas berdasarkan minat tertinggi
        interests = {
            'running': self.profile['interest_jogging'],
            'walking': self.profile['interest_relax'],
            'playing': self.profile['interest_play'],
            'exercise': self.profile['interest_fitness']
        }
        self.chosen_activity = max(interests, key=interests.get)
        
        # 2. Cari tujuan
        target = self.model.find_dest_for_activity(self.chosen_activity, self.start_node)
        
        if target:
            self.target_node = target
            # Durasi simulasi (misal 15-45 menit)
            self.activity_duration = random.randint(15, 45)
            
            self.plan_path(self.pos if self.pos else self.start_node, self.target_node)
        else:
            self.state = "LEAVING" # Kalau gak nemu tujuan, langsung pulang

    def plan_path(self, start, end):
        try:
            self.path = nx.shortest_path(self.model.G, start, end, weight='length')
            if len(self.path) > 0:
                self.path.pop(0)
        except nx.NetworkXNoPath:
            # Jika macet/buntu, langsung teleport pulang/hilang
            self.state = "FINISHED"

    def move(self):
        if self.path:
            next_node = self.path.pop(0)
            self.model.grid.move_agent(self, next_node)
        else:
            # Path habis
            if self.state == "WALKING":
                self.state = "ACTIVITY"
            elif self.state == "LEAVING":
                self.state = "FINISHED" # Sampai di gerbang keluar

    def do_activity(self):
        if self.activity_duration > 0:
            self.activity_duration -= 1
            
            # Logika Lari Loop (Track)
            if self.chosen_activity == 'running' and self.pos in self.model.track_nodes:
                current_idx = self.model.track_nodes.index(self.pos)
                next_idx = (current_idx + 1) % len(self.model.track_nodes)
                next_node = self.model.track_nodes[next_idx]
                self.model.grid.move_agent(self, next_node)
        else:
            # Waktu habis, saatnya pulang
            self.go_home()

    def go_home(self):
        # Kalau sudah jalan pulang atau sudah sampai, abaikan
        if self.state in ["LEAVING", "FINISHED"]:
            return

        # Paksa ubah status jadi Pulang
        self.state = "LEAVING"
        self.chosen_activity = None # Lupakan aktivitas
        self.path = [] # Reset rute lama
        
        # Cari gate terdekat dari posisi sekarang untuk keluar
        closest_gate = None
        min_dist = float('inf')
        
        for gate_node in self.model.gate_nodes:
            try:
                dist = nx.shortest_path_length(self.model.G, self.pos, gate_node, weight='length')
                if dist < min_dist:
                    min_dist = dist
                    closest_gate = gate_node
            except:
                continue
        
        if closest_gate:
            # Hitung rute evakuasi
            self.plan_path(self.pos, closest_gate)
        else:
            # Kalau error/buntu, langsung hilangkan saja
            self.state = "FINISHED"

    def step(self):
        if self.state == "WALKING":
            self.move()
        elif self.state == "ACTIVITY":
            self.do_activity()
        elif self.state == "LEAVING":
            self.move()