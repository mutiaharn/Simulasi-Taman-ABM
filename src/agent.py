import mesa
import networkx as nx

class ParkAgent(mesa.Agent):
    def __init__(self, unique_id, model, start_node, target_node):
        super().__init__(model) # Init bawaan Mesa
        self.unique_id = unique_id
        self.start_node = start_node
        self.target_node = target_node
        
        # Pathfinding: Rute yang akan dilewati
        self.path = [] 
        
    def plan_path(self):
        """Menghitung rute terpendek dari posisi sekarang ke tujuan."""
        try:
            # Menggunakan algoritma Dijkstra dari NetworkX
            # weight='length' artinya mencari jarak meter terpendek, bukan jumlah lompatan
            self.path = nx.shortest_path(
                self.model.G, 
                source=self.start_node, 
                target=self.target_node, 
                weight='length'
            )
            # Hapus node pertama (karena itu posisi dia sekarang)
            if len(self.path) > 0:
                self.path.pop(0)
                
            print(f"Agen {self.unique_id} merencanakan rute: {len(self.path)} langkah.")
            
        except nx.NetworkXNoPath:
            print(f"Agen {self.unique_id} bingung: Tidak ada jalan ke {self.target_node}")

    def move(self):
        """Bergerak satu langkah menuju tujuan."""
        # Kalau belum punya rute, hitung dulu
        if not self.path and self.pos != self.target_node:
            self.plan_path()
            
        # Kalau punya rute, jalan ke node berikutnya
        if self.path:
            next_node = self.path.pop(0)
            self.model.grid.move_agent(self, next_node)
        else:
            # Kalau list path kosong, berarti sudah sampai
            if self.pos == self.target_node:
                # Diam saja (nanti di tahap selanjutnya kita kasih aktivitas)
                pass

    def step(self):
        """Apa yang dilakukan agen setiap 'tik' waktu."""
        self.move()