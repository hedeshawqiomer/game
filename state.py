import random
import math

# === 9 Italian Cities with Fixed Positions and Unique Recruitment ===
# Rome recruits the most. All cities cap at 240 troops.
TROOP_CAP = 240

CITY_DATA = {
    "Turin":    {"x": 215, "y":  95, "recruit": 0.7, "tier": 3},
    "Milan":    {"x": 295, "y":  85, "recruit": 1.2, "tier": 4},
    "Venice":   {"x": 420, "y":  95, "recruit": 0.8, "tier": 3},
    "Genoa":    {"x": 240, "y": 165, "recruit": 0.6, "tier": 2},
    "Florence": {"x": 345, "y": 220, "recruit": 0.9, "tier": 3},
    "Rome":     {"x": 375, "y": 325, "recruit": 1.5, "tier": 5},
    "Naples":   {"x": 440, "y": 400, "recruit": 1.0, "tier": 4},
    "Bari":     {"x": 535, "y": 365, "recruit": 0.5, "tier": 2},
    "Palermo":  {"x": 390, "y": 520, "recruit": 0.5, "tier": 1},
}

class City:
    def __init__(self, name, x, y, owner, troops, recruit_rate, tier):
        self.name = name
        self.x = x
        self.y = y
        self.owner = owner       # "Blue", "Red", "Neutral"
        self.troops = troops
        self.recruit_rate = recruit_rate  # Troops per second
        self.tier = tier         # Visual size: 5=Rome, 1=small
        self.timer = 0.0

class TroopMarch:
    """Animated troop movement from one city to another."""
    def __init__(self, start_city, end_city, troops, owner):
        self.sx, self.sy = start_city.x, start_city.y
        self.ex, self.ey = end_city.x, end_city.y
        self.troops = troops
        self.owner = owner
        self.end_city = end_city
        self.progress = 0.0  # 0=start, 1=arrived
        self.speed = 1.2     # ~0.8 seconds travel time

    def update(self, dt):
        self.progress += self.speed * dt
        return self.progress >= 1.0  # True = arrived

    @property
    def x(self):
        return self.sx + (self.ex - self.sx) * self.progress

    @property
    def y(self):
        return self.sy + (self.ey - self.sy) * self.progress

class GameState:
    def __init__(self):
        self.cities = []
        self.marches = []

    def build_map(self):
        """Create exactly 9 cities. Blue=Turin, Red=Naples, rest=Neutral."""
        self.cities = []
        self.marches = []
        
        for name, data in CITY_DATA.items():
            if name == "Milan":
                owner = "Blue"
                troops = 35
            elif name == "Naples":
                owner = "Red"
                troops = 35
            else:
                owner = "Neutral"
                troops = random.randint(5, 15)
            
            self.cities.append(City(
                name, data["x"], data["y"], owner,
                troops, data["recruit"], data["tier"]
            ))
