import pygame
import sys
import math
from state import LevelState, MapGenerator
from mechanics import Mechanics
from ai import Red_AI_Opponent
from renderer import Renderer

def get_city_at_pos(state, pos):
    for city in state.cities:
        dist = math.hypot(city.x - pos[0], city.y - pos[1])
        if dist <= city.radius:
            return city
    return None

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Conquest of Italy")
    clock = pygame.time.Clock()

    state = LevelState()
    mechanics = Mechanics(state)
    ai = Red_AI_Opponent(state, mechanics)
    renderer = Renderer(screen, state)
    generator = MapGenerator()

    # Initial load
    state.load_cities(generator.generate_level(state.level_number))

    drag_start_city = None
    level_transition_timer = 0
    app_state = "LOBBY"
    deployment_percentage = 0.5

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds

        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if app_state == "LOBBY":
                        state.level_number = 1
                        state.load_cities(generator.generate_level(1))
                        ai.timer = 0.0
                        app_state = "PLAYING"
                            
                    elif app_state in ["GAME_OVER", "VICTORY"]:
                        app_state = "LOBBY"
                        
                    elif app_state == "PLAYING":
                        city = get_city_at_pos(state, event.pos)
                        if city and city.owner == "Blue":
                            drag_start_city = city
                        
            elif event.type == pygame.MOUSEWHEEL:
                if app_state == "PLAYING":
                    if event.y > 0: # Scroll up
                        deployment_percentage = min(1.0, deployment_percentage + 0.25)
                    elif event.y < 0: # Scroll down
                        deployment_percentage = max(0.25, deployment_percentage - 0.25)
                        
            elif event.type == pygame.KEYDOWN:
                if app_state == "PLAYING":
                    if event.key == pygame.K_1:
                        deployment_percentage = 0.25
                    elif event.key == pygame.K_2:
                        deployment_percentage = 0.50
                    elif event.key == pygame.K_3:
                        deployment_percentage = 0.75
                    elif event.key == pygame.K_4:
                        deployment_percentage = 1.0

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if drag_start_city:
                        end_city = get_city_at_pos(state, event.pos)
                        if end_city and end_city != drag_start_city:
                            mechanics.resolve_drag(drag_start_city, end_city, deployment_percentage)
                        drag_start_city = None

        if app_state == "PLAYING":
            mechanics.update_generation(dt)
            mechanics.update_marches(dt)
            ai.update(dt)
            
            # Check win condition
            blue_count = sum(1 for c in state.cities if c.owner == "Blue")
            red_count = sum(1 for c in state.cities if c.owner == "Red")
            
            if blue_count == len(state.cities):
                app_state = "VICTORY"
                    
            if red_count == len(state.cities):
                app_state = "GAME_OVER"
                
            pygame.display.set_caption("Conquest of Italy")

        # Handle Rendering
        if app_state == "LOBBY":
            renderer.render_overlay("CONQUEST OF ITALY", "Click Anywhere to Start")
        else:
            renderer.render(drag_start_city, mouse_pos if drag_start_city else None, deployment_percentage)
            
            if app_state == "GAME_OVER":
                renderer.render_overlay("GAME OVER", "Red has conquered Italy. Click to return to Lobby.")
            elif app_state == "VICTORY":
                renderer.render_overlay("VICTORY!", "You conquered Italy. Click to return to Lobby.")

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
