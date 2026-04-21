import pygame
import os
import math
import random
from state import TROOP_CAP

class Particle:
    """Small visual effect particle for battle impacts."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(40, 120)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.uniform(0.3, 0.8)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(2, 5)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= dt
        return self.life > 0

    def draw(self, screen):
        alpha = max(0, self.life / self.max_life)
        r = max(1, int(self.size * alpha))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), r)


class Renderer:
    def __init__(self, screen, state):
        self.screen = screen
        self.state = state
        pygame.font.init()
        self.font = pygame.font.SysFont("segoeui", 22, bold=True)
        self.name_font = pygame.font.SysFont("segoeui", 16, bold=True)
        self.small_font = pygame.font.SysFont("segoeui", 13)
        self.title_font = pygame.font.SysFont("segoeui", 58, bold=True)
        self.sub_font = pygame.font.SysFont("segoeui", 30)
        self.hud_font = pygame.font.SysFont("segoeui", 18, bold=True)
        
        # Load background map
        self.bg = None
        bg_path = "map_bg.png"
        if os.path.exists(bg_path):
            try:
                bg_img = pygame.image.load(bg_path).convert()
                self.bg = pygame.transform.scale(bg_img, (screen.get_width(), screen.get_height()))
            except Exception:
                pass
        
        self.colors = {
            "Blue": (60, 140, 255),
            "Red": (255, 65, 65),
            "Neutral": (140, 140, 140)
        }
        self.glow_colors = {
            "Blue": (60, 140, 255, 40),
            "Red": (255, 65, 65, 40),
            "Neutral": (140, 140, 140, 20)
        }
        self.dark_colors = {
            "Blue": (30, 80, 180),
            "Red": (180, 35, 35),
            "Neutral": (90, 90, 90)
        }
        
        self.particles = []
        self.time = 0.0  # Global animation timer
        
    def spawn_battle_particles(self, x, y, color, count=15):
        """Spawn explosion particles at a location."""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def _draw_background(self):
        if self.bg:
            self.screen.blit(self.bg, (0, 0))
        else:
            self.screen.fill((20, 25, 30))
            for x in range(0, self.screen.get_width(), 40):
                pygame.draw.line(self.screen, (30, 35, 45), (x, 0), (x, self.screen.get_height()))
            for y in range(0, self.screen.get_height(), 40):
                pygame.draw.line(self.screen, (30, 35, 45), (0, y), (self.screen.get_width(), y))

    def _draw_city_glow(self, city):
        """Draw a soft pulsing glow around owned cities."""
        if city.owner == "Neutral":
            return
        pulse = 0.7 + 0.3 * math.sin(self.time * 2.5 + hash(city.name))
        r = int((city.tier * 8 + 20) * pulse)
        glow_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        gc = self.glow_colors[city.owner]
        pygame.draw.circle(glow_surf, gc, (r, r), r)
        self.screen.blit(glow_surf, (city.x - r, city.y - r))

    def _draw_city(self, city):
        """Draw building shapes based on city tier."""
        color = self.colors[city.owner]
        dark = self.dark_colors[city.owner]
        cx, cy = city.x, city.y
        t = city.tier
        
        # Subtle pulse for owned cities
        scale = 1.0
        if city.owner != "Neutral":
            scale = 1.0 + 0.03 * math.sin(self.time * 3 + hash(city.name))
        
        if t >= 5:
            # ROME — Grand castle with 3 towers
            bw, bh = int(50*scale), int(30*scale)
            pygame.draw.rect(self.screen, dark, (cx-bw//2, cy-bh//2, bw, bh))
            pygame.draw.rect(self.screen, color, (cx-bw//2+2, cy-bh//2+2, bw-4, bh-4))
            # Towers
            for tx_off, th in [(-22, 22), (0, 32), (12, 22)]:
                tw = 12 if tx_off != 0 else 14
                pygame.draw.rect(self.screen, dark, (cx+tx_off-1, cy-bh//2-th-1, tw+2, th+2))
                pygame.draw.rect(self.screen, color, (cx+tx_off, cy-bh//2-th, tw, th))
            # Battlements on center tower
            for bx in range(cx-5, cx+9, 4):
                pygame.draw.rect(self.screen, dark, (bx, cy-bh//2-35, 3, 4))
            pygame.draw.rect(self.screen, (255,255,255), (cx-bw//2, cy-bh//2, bw, bh), 1)
            
        elif t >= 4:
            # MAJOR CITY — 2 towers
            bw, bh = int(40*scale), int(24*scale)
            pygame.draw.rect(self.screen, dark, (cx-bw//2, cy-bh//2, bw, bh))
            pygame.draw.rect(self.screen, color, (cx-bw//2+2, cy-bh//2+2, bw-4, bh-4))
            for tx_off in [-14, 8]:
                pygame.draw.rect(self.screen, dark, (cx+tx_off-1, cy-bh//2-19, 12, 19))
                pygame.draw.rect(self.screen, color, (cx+tx_off, cy-bh//2-18, 10, 18))
            pygame.draw.rect(self.screen, (255,255,255), (cx-bw//2, cy-bh//2, bw, bh), 1)
            
        elif t >= 3:
            # MEDIUM — 1 tower
            bw, bh = int(32*scale), int(20*scale)
            pygame.draw.rect(self.screen, dark, (cx-bw//2, cy-bh//2, bw, bh))
            pygame.draw.rect(self.screen, color, (cx-bw//2+2, cy-bh//2+2, bw-4, bh-4))
            pygame.draw.rect(self.screen, dark, (cx-6, cy-bh//2-17, 12, 17))
            pygame.draw.rect(self.screen, color, (cx-5, cy-bh//2-16, 10, 16))
            pygame.draw.rect(self.screen, (255,255,255), (cx-bw//2, cy-bh//2, bw, bh), 1)
            
        elif t >= 2:
            # SMALL TOWN — House with roof
            bw, bh = int(26*scale), int(16*scale)
            pygame.draw.rect(self.screen, dark, (cx-bw//2, cy-bh//2, bw, bh))
            pygame.draw.rect(self.screen, color, (cx-bw//2+2, cy-bh//2+2, bw-4, bh-4))
            pts = [(cx-bw//2-2, cy-bh//2), (cx, cy-bh//2-12), (cx+bw//2+2, cy-bh//2)]
            pygame.draw.polygon(self.screen, dark, pts)
            pygame.draw.polygon(self.screen, color, [(cx-bw//2, cy-bh//2), (cx, cy-bh//2-10), (cx+bw//2, cy-bh//2)])
            pygame.draw.rect(self.screen, (255,255,255), (cx-bw//2, cy-bh//2, bw, bh), 1)
        else:
            # VILLAGE — Tiny house
            bw, bh = int(20*scale), int(14*scale)
            pygame.draw.rect(self.screen, dark, (cx-bw//2, cy-bh//2, bw, bh))
            pygame.draw.rect(self.screen, color, (cx-bw//2+2, cy-bh//2+2, bw-4, bh-4))
            pts = [(cx-bw//2-2, cy-bh//2), (cx, cy-bh//2-10), (cx+bw//2+2, cy-bh//2)]
            pygame.draw.polygon(self.screen, dark, pts)
            pygame.draw.polygon(self.screen, color, [(cx-bw//2, cy-bh//2), (cx, cy-bh//2-8), (cx+bw//2, cy-bh//2)])
            pygame.draw.rect(self.screen, (255,255,255), (cx-bw//2, cy-bh//2, bw, bh), 1)

    def _draw_drag_line(self, start_city, mouse_pos):
        """Draw an animated dashed arrow line from city to mouse."""
        color = self.colors[start_city.owner]
        sx, sy = start_city.x, start_city.y
        ex, ey = mouse_pos
        dx, dy = ex - sx, ey - sy
        length = math.hypot(dx, dy)
        if length < 1:
            return
        
        # Animated dashes
        dash_len = 12
        gap_len = 8
        offset = (self.time * 80) % (dash_len + gap_len)
        
        ux, uy = dx/length, dy/length
        pos = offset
        while pos < length:
            s = pos
            e = min(pos + dash_len, length)
            p1 = (int(sx + ux*s), int(sy + uy*s))
            p2 = (int(sx + ux*e), int(sy + uy*e))
            pygame.draw.line(self.screen, color, p1, p2, 3)
            pos += dash_len + gap_len
        
        # Arrowhead
        if length > 30:
            arrow_size = 10
            angle = math.atan2(dy, dx)
            p1 = (int(ex - arrow_size * math.cos(angle - 0.4)), int(ey - arrow_size * math.sin(angle - 0.4)))
            p2 = (int(ex - arrow_size * math.cos(angle + 0.4)), int(ey - arrow_size * math.sin(angle + 0.4)))
            pygame.draw.polygon(self.screen, color, [(ex, ey), p1, p2])

    def _draw_hud(self, deployment_pct):
        """Draw top status bar and bottom deployment indicator."""
        blue_count = sum(1 for c in self.state.cities if c.owner == "Blue")
        red_count = sum(1 for c in self.state.cities if c.owner == "Red")
        neutral_count = sum(1 for c in self.state.cities if c.owner == "Neutral")
        
        # Top HUD bar
        hud_surf = pygame.Surface((self.screen.get_width(), 32), pygame.SRCALPHA)
        hud_surf.fill((0, 0, 0, 160))
        self.screen.blit(hud_surf, (0, 0))
        
        blue_text = self.hud_font.render(f"  YOU: {blue_count} cities", True, (100, 180, 255))
        red_text = self.hud_font.render(f"BOT: {red_count} cities  ", True, (255, 100, 100))
        neutral_text = self.hud_font.render(f"Neutral: {neutral_count}", True, (180, 180, 180))
        
        self.screen.blit(blue_text, (10, 6))
        self.screen.blit(neutral_text, (self.screen.get_width()//2 - neutral_text.get_width()//2, 6))
        self.screen.blit(red_text, (self.screen.get_width() - red_text.get_width() - 10, 6))
        
        # Bottom deployment bar
        bot_surf = pygame.Surface((280, 32), pygame.SRCALPHA)
        bot_surf.fill((0, 0, 0, 160))
        self.screen.blit(bot_surf, (0, self.screen.get_height()-35))
        
        pct_text = f" Deploy: {int(deployment_pct * 100)}%  [Scroll / 1-4]"
        pct_s = self.hud_font.render(pct_text, True, (255, 255, 200))
        self.screen.blit(pct_s, (10, self.screen.get_height() - 30))

    def render(self, dt, drag_start_city=None, mouse_pos=None, deployment_pct=0.5):
        self.time += dt
        self._draw_background()

        # Draw road connections
        for i, a in enumerate(self.state.cities):
            for j, b in enumerate(self.state.cities):
                if i < j:
                    dist = math.hypot(a.x - b.x, a.y - b.y)
                    if dist < 350:
                        pygame.draw.line(self.screen, (55, 50, 40), (a.x, a.y), (b.x, b.y), 1)

        # Draw city glows
        for city in self.state.cities:
            self._draw_city_glow(city)

        # Draw animated drag line
        if drag_start_city and mouse_pos:
            self._draw_drag_line(drag_start_city, mouse_pos)

        # Draw cities
        for city in self.state.cities:
            self._draw_city(city)
            
            # City name
            name_s = self.name_font.render(city.name, True, (255, 255, 230))
            nh = 52 if city.tier >= 5 else 40 if city.tier >= 4 else 32 if city.tier >= 3 else 26
            self.screen.blit(name_s, (city.x - name_s.get_width()//2, city.y - nh))

            # Troop count
            troop_s = self.font.render(str(int(city.troops)), True, (255, 255, 255))
            self.screen.blit(troop_s, (city.x - troop_s.get_width()//2, city.y - troop_s.get_height()//2))
            
            # Recruit rate
            rate_s = self.small_font.render(f"+{city.recruit_rate}/s", True, (160, 240, 160))
            bh = 20 if city.tier >= 3 else 14
            self.screen.blit(rate_s, (city.x - rate_s.get_width()//2, city.y + bh))

        # Draw troop marches with trailing particles
        for march in self.state.marches:
            color = self.colors.get(march.owner, (200, 200, 200))
            mx, my = int(march.x), int(march.y)
            
            # Trail effect — small fading dots behind the march
            trail_count = 5
            for t in range(trail_count):
                tp = max(0, march.progress - t * 0.04)
                tx = int(march.sx + (march.ex - march.sx) * tp)
                ty = int(march.sy + (march.ey - march.sy) * tp)
                tr = max(1, 4 - t)
                alpha_color = tuple(max(0, c - t*40) for c in color)
                pygame.draw.circle(self.screen, alpha_color, (tx, ty), tr)
            
            # Main march circle
            pygame.draw.circle(self.screen, color, (mx, my), 11)
            pygame.draw.circle(self.screen, (255, 255, 255), (mx, my), 11, 2)
            mt = self.small_font.render(str(march.troops), True, (255, 255, 255))
            self.screen.blit(mt, (mx - mt.get_width()//2, my - mt.get_height()//2))

        # Draw particles
        alive = []
        for p in self.particles:
            if p.update(dt):
                p.draw(self.screen)
                alive.append(p)
        self.particles = alive

        # HUD
        self._draw_hud(deployment_pct)

    def render_overlay(self, main_text, sub_text=""):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        t1 = self.title_font.render(main_text, True, (255, 255, 255))
        self.screen.blit(t1, (self.screen.get_width()//2 - t1.get_width()//2, self.screen.get_height()//2 - 50))
        
        if sub_text:
            t2 = self.sub_font.render(sub_text, True, (200, 200, 200))
            self.screen.blit(t2, (self.screen.get_width()//2 - t2.get_width()//2, self.screen.get_height()//2 + 20))
