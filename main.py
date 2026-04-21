import pygame
import sys
import math
from state import GameState
from mechanics import Mechanics
from ai import Red_AI
from renderer import Renderer

def get_city_at_pos(state, pos):
    """Check if a click is near a city. Uses tier-based hitbox."""
    for city in state.cities:
        hitbox = 30 if city.tier >= 4 else 22
        if math.hypot(city.x - pos[0], city.y - pos[1]) <= hitbox:
            return city
    return None

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Conquest of Italy")
    clock = pygame.time.Clock()

    state = GameState()
    mechanics = Mechanics(state)
    ai = Red_AI(state, mechanics)
    renderer = Renderer(screen, state)
    mechanics.renderer = renderer  # Link for battle effects

    # Start at lobby
    app_state = "LOBBY"
    drag_start_city = None
    deployment_pct = 0.5

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if app_state == "LOBBY":
                    state.build_map()
                    ai.timer = 0.0
                    app_state = "PLAYING"

                elif app_state in ["GAME_OVER", "VICTORY"]:
                    app_state = "LOBBY"

                elif app_state == "PLAYING":
                    city = get_city_at_pos(state, event.pos)
                    if city and city.owner == "Blue":
                        drag_start_city = city

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drag_start_city:
                    end_city = get_city_at_pos(state, event.pos)
                    if end_city and end_city != drag_start_city:
                        mechanics.send_troops(drag_start_city, end_city, deployment_pct)
                    drag_start_city = None

            elif event.type == pygame.MOUSEWHEEL and app_state == "PLAYING":
                if event.y > 0:
                    deployment_pct = min(1.0, deployment_pct + 0.25)
                elif event.y < 0:
                    deployment_pct = max(0.25, deployment_pct - 0.25)

            elif event.type == pygame.KEYDOWN and app_state == "PLAYING":
                if event.key == pygame.K_1: deployment_pct = 0.25
                elif event.key == pygame.K_2: deployment_pct = 0.50
                elif event.key == pygame.K_3: deployment_pct = 0.75
                elif event.key == pygame.K_4: deployment_pct = 1.0

        # === Game Logic ===
        if app_state == "PLAYING":
            mechanics.update_recruitment(dt)
            mechanics.update_marches(dt)
            ai.update(dt)

            blue = sum(1 for c in state.cities if c.owner == "Blue")
            red = sum(1 for c in state.cities if c.owner == "Red")

            # Instant win/lose when a side loses all cities
            if red == 0:
                app_state = "VICTORY"
            elif blue == 0:
                app_state = "GAME_OVER"

        # === Rendering ===
        if app_state == "LOBBY":
            renderer.render(dt)
            renderer.render_overlay("CONQUEST OF ITALY", "Click to Start")
        else:
            renderer.render(dt, drag_start_city, mouse_pos if drag_start_city else None, deployment_pct)
            if app_state == "GAME_OVER":
                renderer.render_overlay("GAME OVER", "Red conquered Italy. Click to return.")
            elif app_state == "VICTORY":
                renderer.render_overlay("VICTORY!", "You conquered Italy! Click to return.")

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
