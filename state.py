import random
import math

# City tiers: (radius, generation_rate) — bigger cities recruit faster
CITY_TIERS = {
    "Rome":      {"radius": 40, "gen_rate": 1.2},
    "Milan":     {"radius": 36, "gen_rate": 1.0},
    "Naples":    {"radius": 34, "gen_rate": 0.9},
    "Turin":     {"radius": 32, "gen_rate": 0.8},
    "Florence":  {"radius": 32, "gen_rate": 0.8},
    "Venice":    {"radius": 32, "gen_rate": 0.8},
    "Genoa":     {"radius": 28, "gen_rate": 0.6},
    "Bologna":   {"radius": 28, "gen_rate": 0.6},
    "Palermo":   {"radius": 28, "gen_rate": 0.6},
    "Bari":      {"radius": 24, "gen_rate": 0.5},
    "Catania":   {"radius": 24, "gen_rate": 0.5},
    "Verona":    {"radius": 24, "gen_rate": 0.5},
}

# Fallback for any city not in the table
DEFAULT_TIER = {"radius": 22, "gen_rate": 0.4}

class City:
    def __init__(self, name, x, y, owner, initial_troops):
        self.name = name
        self.x = x
        self.y = y
        self.owner = owner  # "Blue", "Red", "Neutral"
        self.troops = initial_troops
        tier = CITY_TIERS.get(name, DEFAULT_TIER)
        self.radius = tier["radius"]
        self.generation_rate = tier["gen_rate"]
        self.timer = 0.0

class TroopMarch:
    """Animated troop movement from one city to another."""
    def __init__(self, start_city, end_city, troops, owner):
        self.sx, self.sy = start_city.x, start_city.y
        self.ex, self.ey = end_city.x, end_city.y
        self.troops = troops
        self.owner = owner
        self.end_city = end_city
        self.progress = 0.0  # 0 = start, 1 = arrived
        self.speed = 1.5     # Takes ~0.67 seconds to arrive

    def update(self, dt):
        self.progress += self.speed * dt
        if self.progress >= 1.0:
            self.progress = 1.0
            return True  # Arrived
        return False

    @property
    def x(self):
        return self.sx + (self.ex - self.sx) * self.progress

    @property
    def y(self):
        return self.sy + (self.ey - self.sy) * self.progress

class LevelState:
    def __init__(self):
        self.cities = []
        self.marches = []  # Active troop animations
        self.level_number = 1
        
    def load_cities(self, cities):
        self.cities = cities
        self.marches = []

class MapGenerator:
    def __init__(self):
        # Use the tiered city names first, then extras
        self.tier_names = list(CITY_TIERS.keys())
        self.extra_names = ["Messina", "Padua", "Trieste", "Brescia",
                            "Parma", "Taranto", "Modena", "Ravenna",
                            "Livorno", "Rimini", "Ferrara", "Sassari"]

    def generate_level(self, level):
        num_cities = min(6 + (level * 2), 20)
        num_red = min(1 + (level // 2), 5)
        num_blue = 1
        
        # Shuffle names: prioritize tiered cities, then extras
        all_names = self.tier_names[:] + self.extra_names[:]
        random.shuffle(all_names)
        
        cities = []
        width, height = 800, 600
        margin = 100
        
        attempts = 0
        name_idx = 0
        while len(cities) < num_cities and attempts < 1000:
            attempts += 1
            x = random.randint(margin, width - margin)
            y = random.randint(margin, height - margin)
            
            # Check overlap spacing
            overlap = False
            for c in cities:
                if math.hypot(c.x - x, c.y - y) < 130:
                    overlap = True
                    break
            
            if overlap:
                continue
            
            name = all_names[name_idx % len(all_names)]
            name_idx += 1
                
            if len(cities) < num_blue:
                owner = "Blue"
                troops = 40
            elif len(cities) < num_blue + num_red:
                owner = "Red"
                troops = 15 + level
            else:
                owner = "Neutral"
                troops = random.randint(5, 15)
                
            cities.append(City(name, x, y, owner, troops))
            
        return cities
