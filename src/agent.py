import mesa
import networkx as nx
import random

class ParkAgent(mesa.Agent):
    def __init__(self, unique_id, model, start_node, profile, initial_interest=None):
        super().__init__(model)
        self.unique_id = unique_id
        self.start_node = start_node
        self.profile = profile
        
        # Atribut Dinamis
        self.state = "DECIDING" # DECIDING, WALKING, ACTIVITY, LEAVING, FINISHED
        self.path = []
        self.target_zone_id = None
        self.target_node = None
        self.current_activity = initial_interest if initial_interest else "walking"
        self.activity_duration = 0
        
        # Normalisasi profil (jika data string/kotor)
        self.crowd_dislike = float(profile.get('crowd_dislike', 3)) / 5.0 # Skala 0-1
        self.heat_dislike = float(profile.get('heat_dislike', 3)) / 5.0   # Skala 0-1

    def make_decision(self):
        """
        METODE PENGAMBILAN KEPUTUSAN BERBASIS FILTER (4 TAHAP)
        """
        # --- 1. Identifikasi Kebutuhan ---
        # Jika baru spawn, pakai current_activity. Jika selesai, pilih baru.
        # (Sederhana: Pilih random based on interest profile)
        if self.state != "DECIDING": 
            # Logic pilih aktivitas selanjutnya
            interests = {
                'running': self.profile['interest_jogging'],
                'walking': self.profile['interest_relax'],
                'playing': self.profile['interest_play'],
                'exercise': self.profile['interest_fitness'],
                'relax': self.profile['interest_relax']
            }
            # Pilih aktivitas dengan bobot tertinggi + sedikit random
            self.current_activity = max(interests, key=lambda k: interests[k] + random.uniform(0, 2))

        # --- CEK TRIGER LINGKUNGAN (Override) ---
        is_raining = self.model.current_env['rain_flag']
        if is_raining:
            # Override: Cari Shelter atau Pulang
            self.current_activity = 'shelter_seeking'
        
        # --- 2. Filter Kandidat Zona ---
        candidates = []
        
        if self.current_activity == 'shelter_seeking':
            # Cari zona bertipe 'gazebo', 'public_toilet', atau 'gate' (pulang)
            candidates = [z for z in self.model.zone_map.values() 
                          if z['zone_type'] in ['gazebo', 'public_toilet', 'gate']]
        else:
            # Cari zona yang mendukung aktivitas
            for z in self.model.zone_map.values():
                if self.current_activity in z.get('supported_activities', []):
                    candidates.append(z)

        # Jika tidak ada kandidat (misal mau lari tapi gak ada track), fallback ke walking
        if not candidates and self.current_activity != 'shelter_seeking':
            self.current_activity = 'walking'
            candidates = [z for z in self.model.zone_map.values() if 'walking' in z.get('supported_activities', [])]

        # --- 3. Filter Penalti (Eliminasi Kritis) ---
        final_candidates = []
        
        current_temp = self.model.current_env['temperature_index']
        
        for z in candidates:
            # A. Penalti Keramaian
            capacity = float(z.get('zone_max_capacity', 20))
            current_pop = z.get('current_agents', 0)
            crowd_ratio = min(current_pop / capacity, 1.0)
            
            # Logika: Jika rasio keramaian > toleransi ketidaksukaan agen, eliminasi
            # (Kecuali hujan/shelter, darurat abaikan keramaian)
            if not is_raining and crowd_ratio > (1.0 - self.crowd_dislike):
                continue # Skip zona ini, terlalu ramai buat saya

            # B. Penalti Panas
            # Jika panas tinggi (>0.7) DAN saya benci panas, hindari zona terbuka
            if not is_raining and current_temp > 0.7 and self.heat_dislike > 0.6:
                if z['zone_type'] in ['track', 'plaza', 'playground']: # Asumsi ini zona panas
                    continue 

            final_candidates.append(z)

        # Kalau semua kena eliminasi, paksa ambil 1 dari kandidat awal (terpaksa)
        if not final_candidates:
            final_candidates = candidates

        # --- 4. Keputusan Akhir ---
        if final_candidates:
            # Pilih yang amenities_score tertinggi atau paling dekat
            # Kita pakai random choice weighted by amenities untuk variasi
            best_zone = max(final_candidates, key=lambda z: z.get('amenities_score', 0.5) + random.random())
            
            self.target_zone_id = best_zone['zone_id']
            self.target_node = best_zone['nav_node']
            
            # Rencanakan jalan
            self.plan_path(self.pos, self.target_node)
            self.state = "WALKING"
        else:
            # Bingung total -> Pulang
            self.go_home()

    def plan_path(self, start, end):
        try:
            self.path = nx.shortest_path(self.model.G, start, end, weight='length')
            if self.path: self.path.pop(0)
        except:
            self.state = "FINISHED"

    def move(self):
        if self.path:
            next_node = self.path.pop(0)
            self.model.grid.move_agent(self, next_node)
        else:
            # Sampai tujuan
            if self.target_zone_id:
                self.state = "ACTIVITY"
                # Set durasi berdasarkan Activity Profile
                rules = self.model.activity_rules.get(self.current_activity, {})
                base_dwell = int(rules.get('base_dwell_min', 15))
                self.activity_duration = base_dwell + random.randint(-5, 5)
            else:
                self.state = "FINISHED" # Sampai di gate pulang

    def do_activity(self):
        # Cek kondisi darurat (Hujan Tiba-tiba)
        if self.model.current_env['rain_flag'] and self.current_activity != 'shelter_seeking':
             # Cek apakah zona sekarang aman (shelter)?
             current_zone = self.model.zone_map.get(self.target_zone_id)
             if current_zone and current_zone['zone_type'] not in ['gazebo', 'public_toilet']:
                 # Panik! Cari shelter baru
                 self.make_decision()
                 return

        if self.activity_duration > 0:
            self.activity_duration -= 1
            
            # Logika Visualisasi Track Loop (Optional)
            if self.current_activity == 'running' and self.pos in self.model.track_nodes:
                 curr = self.model.track_nodes.index(self.pos)
                 nxt = self.model.track_nodes[(curr+1)%len(self.model.track_nodes)]
                 self.model.grid.move_agent(self, nxt)
        else:
            # Selesai aktivitas
            # Jika tadi shelter seeking dan hujan reda, atau aktivitas biasa selesai
            if self.current_activity == 'shelter_seeking' and self.model.current_env['rain_flag']:
                return # Tetap berteduh
            
            # Decide next move (Activity lain atau Pulang)
            # Simple logic: Chance pulang meningkat seiring waktu
            if random.random() < 0.3: 
                self.go_home()
            else:
                self.state = "DECIDING" # Memicu make_decision() di step berikutnya

    def go_home(self):
        self.current_activity = 'leaving'
        # Cari gate terdekat
        closest_gate = None; min_d = float('inf')
        for g in self.model.gate_nodes:
            try:
                d = nx.shortest_path_length(self.model.G, self.pos, g, weight='length')
                if d < min_d: min_d = d; closest_gate = g
            except: continue
            
        if closest_gate:
            self.target_zone_id = None # Penanda mau keluar
            self.target_node = closest_gate
            self.plan_path(self.pos, closest_gate)
            self.state = "LEAVING"
        else:
            self.state = "FINISHED"

    def step(self):
        if self.state == "DECIDING":
            self.make_decision()
        elif self.state in ["WALKING", "LEAVING"]:
            self.move()
        elif self.state == "ACTIVITY":
            self.do_activity()