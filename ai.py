class Red_AI:
    def __init__(self, state, mechanics):
        self.state = state
        self.mechanics = mechanics
        self.timer = 0.0
        self.action_interval = 4.5  # AI acts every 4.5 seconds

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.action_interval:
            self.timer = 0.0
            self.execute_turn()

    def execute_turn(self):
        """AI picks the best nearby target it can beat."""
        red_cities = [c for c in self.state.cities if c.owner == "Red" and c.troops > 8]
        targets = [c for c in self.state.cities if c.owner != "Red"]

        if not red_cities or not targets:
            return

        best_attack = None
        best_score = -9999

        for rc in red_cities:
            for tc in targets:
                dist = ((rc.x - tc.x)**2 + (rc.y - tc.y)**2)**0.5
                if dist < 450:
                    # AI sends 55%, needs moderate advantage
                    advantage = (rc.troops * 0.55) - tc.troops
                    if advantage > 3 and advantage > best_score:
                        best_score = advantage
                        best_attack = (rc, tc)

        if best_attack:
            self.mechanics.send_troops(best_attack[0], best_attack[1], 0.55)
