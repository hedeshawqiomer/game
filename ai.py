class Red_AI_Opponent:
    def __init__(self, state, mechanics):
        self.state = state
        self.mechanics = mechanics
        self.timer = 0.0
        self.action_interval = 4.0  # Slowed down from 2 to 4 seconds for balance

    def update(self, dt):
        """Asynchronous update loop throttling calculation."""
        self.timer += dt
        if self.timer >= self.action_interval:
            self.timer = 0.0
            self.execute_turn()

    def execute_turn(self):
        """State machine for Red AI: target scanning and execution."""
        red_cities = [c for c in self.state.cities if c.owner == "Red" and c.troops > 1]
        other_cities = [c for c in self.state.cities if c.owner != "Red"]

        if not red_cities or not other_cities:
            return  # Game over or cannot attack

        best_attack = None
        best_score = -9999

        for rc in red_cities:
            for oc in other_cities:
                # Assess distance
                dist = ((rc.x - oc.x)**2 + (rc.y - oc.y)**2)**0.5
                if dist < 450:  # Distance filter to favor nearby attacks
                    # Vulnerability Assessment
                    advantage = (rc.troops - 1) - oc.troops
                    if advantage > 0:
                        if advantage > best_score:
                            best_score = advantage
                            best_attack = (rc, oc)

        if best_attack:
            # Execution
            self.mechanics.resolve_drag(best_attack[0], best_attack[1], 1.0)
