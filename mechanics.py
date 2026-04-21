from state import TroopMarch, TROOP_CAP

class Mechanics:
    def __init__(self, state):
        self.state = state
        self.renderer = None  # Set by main.py for battle effects

    def update_recruitment(self, dt):
        """Recruit troops over time. Stops at TROOP_CAP (240)."""
        for city in self.state.cities:
            if city.owner != "Neutral" and city.troops < TROOP_CAP:
                city.timer += dt
                troops_to_add = int(city.timer * city.recruit_rate)
                if troops_to_add > 0:
                    city.troops = min(city.troops + troops_to_add, TROOP_CAP)
                    city.timer -= (troops_to_add / city.recruit_rate)

    def update_marches(self, dt):
        """Move all active marches. Resolve combat on arrival."""
        arrived = []
        for march in self.state.marches:
            if march.update(dt):
                arrived.append(march)
        
        for march in arrived:
            self.state.marches.remove(march)
            self._resolve_arrival(march)

    def _resolve_arrival(self, march):
        """Combat math when troops reach their target."""
        target = march.end_city
        if march.owner == target.owner:
            # Reinforcement — cap at 240
            target.troops = min(target.troops + march.troops, TROOP_CAP)
        else:
            # Combat — spawn battle particles
            if self.renderer:
                color = (255, 200, 50)  # Golden explosion
                self.renderer.spawn_battle_particles(target.x, target.y, color, 20)
            if march.troops > target.troops:
                target.owner = march.owner
                target.troops = march.troops - target.troops
            else:
                target.troops -= march.troops

    def send_troops(self, start_city, end_city, percentage=0.5):
        """Send a percentage of troops as an animated march."""
        if start_city == end_city or start_city.troops <= 1:
            return
            
        send_count = int(start_city.troops * percentage)
        
        # Always leave at least 1 troop behind
        if send_count >= start_city.troops:
            send_count = start_city.troops - 1
        if send_count < 1:
            return
            
        start_city.troops -= send_count
        march = TroopMarch(start_city, end_city, send_count, start_city.owner)
        self.state.marches.append(march)
