from state import TroopMarch

class Mechanics:
    def __init__(self, state):
        self.state = state

    def update_generation(self, dt):
        """Generates troops over time for non-neutral cities."""
        for city in self.state.cities:
            if city.owner != "Neutral":
                city.timer += dt
                troops_to_add = int(city.timer * city.generation_rate)
                if troops_to_add > 0:
                    city.troops += troops_to_add
                    city.timer -= (troops_to_add / city.generation_rate)

    def update_marches(self, dt):
        """Move all active troop marches and resolve arrivals."""
        arrived = []
        for march in self.state.marches:
            if march.update(dt):
                arrived.append(march)
        
        for march in arrived:
            self.state.marches.remove(march)
            self._resolve_arrival(march)

    def _resolve_arrival(self, march):
        """Combat resolution when marching troops arrive at a city."""
        end_city = march.end_city
        if march.owner == end_city.owner:
            # Reinforcement
            end_city.troops += march.troops
        else:
            # Combat
            if march.troops > end_city.troops:
                end_city.owner = march.owner
                end_city.troops = march.troops - end_city.troops
            else:
                end_city.troops -= march.troops

    def resolve_drag(self, start_city, end_city, percentage=0.5):
        """Sends troops as an animated march instead of instant transfer."""
        if start_city == end_city:
            return
        
        if start_city.troops <= 1:
            return
            
        attacking_troops = int(start_city.troops * percentage)
        
        # Always leave at least 1 troop behind
        if attacking_troops >= start_city.troops:
            attacking_troops = start_city.troops - 1
            
        if attacking_troops < 1:
            return
            
        start_city.troops -= attacking_troops
        
        # Create animated march instead of instant resolution
        march = TroopMarch(start_city, end_city, attacking_troops, start_city.owner)
        self.state.marches.append(march)
