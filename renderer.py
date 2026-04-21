import pygame
import os
import math

class Renderer:
    def __init__(self, screen, state):
        self.screen = screen
        self.state = state
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 28)
        self.name_font = pygame.font.SysFont(None, 18)
        self.small_font = pygame.font.SysFont(None, 16)
        
        self.bg = None
        bg_path = "map_bg.png"
        if os.path.exists(bg_path):
            try:
                bg_img = pygame.image.load(bg_path).convert()
                self.bg = pygame.transform.scale(bg_img, (screen.get_width(), screen.get_height()))
            except Exception:
                pass
        
        self.colors = {
            "Blue": (50, 150, 255),
            "Red": (255, 70, 70),
            "Neutral": (120, 120, 120)
        }
        
    def draw_grid(self):
        if self.bg:
            self.screen.blit(self.bg, (0, 0))
        else:
            self.screen.fill((20, 25, 30))
            for x in range(0, self.screen.get_width(), 40):
                pygame.draw.line(self.screen, (30, 35, 45), (x, 0), (x, self.screen.get_height()))
            for y in range(0, self.screen.get_height(), 40):
                pygame.draw.line(self.screen, (30, 35, 45), (0, y), (self.screen.get_width(), y))

    def _draw_city_shape(self, city):
        """Draw city as a shape scaled by its historical influence (radius)."""
        color = self.colors[city.owner]
        r = city.radius
        cx, cy = city.x, city.y
        
        if r >= 38:
            # Capital city (Rome): draw a star shape
            points = []
            for i in range(10):
                angle = math.radians(i * 36 - 90)
                dist = r if i % 2 == 0 else r * 0.55
                points.append((cx + dist * math.cos(angle), cy + dist * math.sin(angle)))
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, (255, 255, 255), points, 2)
        elif r >= 32:
            # Major city: draw a hexagon
            points = []
            for i in range(6):
                angle = math.radians(i * 60 - 30)
                points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, (255, 255, 255), points, 2)
        elif r >= 26:
            # Medium city: draw a diamond
            points = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, (255, 255, 255), points, 2)
        else:
            # Small city: draw a square
            rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)

    def render(self, drag_start_city=None, mouse_pos=None, deployment_percentage=0.5):
        self.draw_grid()

        # Draw decorative connections between cities
        for i, city_a in enumerate(self.state.cities):
            for j, city_b in enumerate(self.state.cities):
                if i < j:
                    dist = ((city_a.x - city_b.x)**2 + (city_a.y - city_b.y)**2)**0.5
                    if dist < 400:
                        pygame.draw.line(self.screen, (60, 60, 70), (city_a.x, city_a.y), (city_b.x, city_b.y), 1)

        # Render drag indicator
        if drag_start_city and mouse_pos:
            pygame.draw.line(self.screen, self.colors[drag_start_city.owner], 
                             (drag_start_city.x, drag_start_city.y), mouse_pos, 4)

        # Render cities
        for city in self.state.cities:
            self._draw_city_shape(city)
            
            # City name text
            name_surf = self.name_font.render(city.name, True, (240, 240, 240))
            self.screen.blit(name_surf, (city.x - name_surf.get_width()//2, city.y - city.radius - 15))

            # Troop count text
            troop_surf = self.font.render(str(int(city.troops)), True, (255, 255, 255))
            self.screen.blit(troop_surf, (city.x - troop_surf.get_width()//2, city.y - troop_surf.get_height()//2))
            
            # Recruitment rate text
            rate_text = f"+{city.generation_rate}/s"
            rate_surf = self.small_font.render(rate_text, True, (180, 255, 180))
            self.screen.blit(rate_surf, (city.x - rate_surf.get_width()//2, city.y + city.radius + 5))

        # Draw animated troop marches
        for march in self.state.marches:
            color = self.colors.get(march.owner, (200, 200, 200))
            mx, my = int(march.x), int(march.y)
            # Draw a small moving circle with troop count
            pygame.draw.circle(self.screen, color, (mx, my), 12)
            pygame.draw.circle(self.screen, (255, 255, 255), (mx, my), 12, 2)
            mt = self.small_font.render(str(march.troops), True, (255, 255, 255))
            self.screen.blit(mt, (mx - mt.get_width()//2, my - mt.get_height()//2))

        # Draw deployment percentage indicator
        pct_text = f"Deployment: {int(deployment_percentage * 100)}%  [Scroll or 1-4]"
        pct_surf = self.font.render(pct_text, True, (255, 255, 200))
        self.screen.blit(pct_surf, (20, self.screen.get_height() - 40))

    def render_overlay(self, main_text, sub_text=""):
        # Draw semi-transparent dark overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) 
        self.screen.blit(overlay, (0, 0))
        
        # Draw big text
        t1 = pygame.font.SysFont(None, 80).render(main_text, True, (255, 255, 255))
        self.screen.blit(t1, (self.screen.get_width()//2 - t1.get_width()//2, self.screen.get_height()//2 - 50))
        
        # Draw small instruction text
        if sub_text:
            t2 = pygame.font.SysFont(None, 40).render(sub_text, True, (200, 200, 200))
            self.screen.blit(t2, (self.screen.get_width()//2 - t2.get_width()//2, self.screen.get_height()//2 + 30))
