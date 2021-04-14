import pygame

from models import Asteroid, Spaceship
from utils import load_sprite, get_random_position, print_text

# Class to handle the main game and gameplay loop
class SpaceRocks:
    # Class variables
    MIN_ASTEROID_DISTANCE = 250

    # Constructor for instance of our gameplay handler classs
    def __init__(self):
        # Call a private initialization method
        self._init_pygame()
        self.screen = pygame.display.set_mode((800, 600))
        self.background = load_sprite("space", False)
        self.clock = pygame.time.Clock() # Ensure stable FPS
        self.font = pygame.font.Font(None, 64)
        self.message = ""

        self.asteroids = []
        self.bullets = []
        self.spaceship = Spaceship((400, 300), self.bullets.append)

        for _ in range(6):
            while True:
                position = get_random_position(self.screen)
                if (
                    position.distance_to(self.spaceship.position) > self.MIN_ASTEROID_DISTANCE
                ):
                    break

            self.asteroids.append(Asteroid(position, self.asteroids.append))

    # Main game loop happening in three parts: handle inputs,
    # process game logic, and then draw to the screen
    def main_loop(self):
        while True:
            self._handle_input()
            self._process_game_logic()
            self._draw()

    # Private initialization method
    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Space Rocks")

    # Handle inputs, using the arrow keys and space bar
    def _handle_input(self):
        # Get the events from pygame module
        for event in pygame.event.get():
            # Allow user to quit the game
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()
            elif (
                self.spaceship
                and event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
            ):
                self.spaceship.shoot()

        # Get dictionary of pressed keys
        is_key_pressed = pygame.key.get_pressed()

        # If the spaceship isn't destroyed
        if self.spaceship:
            # Rotate the ship object appropriately
            if is_key_pressed[pygame.K_RIGHT]:
                self.spaceship.rotate(clockwise = True)
            elif is_key_pressed[pygame.K_LEFT]:
                self.spaceship.rotate(clockwise = False)
            
            # Accelerate the ship
            if is_key_pressed[pygame.K_UP]:
                self.spaceship.accelerate()
        
    # handle the game logic, account for collisions, etc.
    def _process_game_logic(self):
        for game_object in self._get_game_objects():
            game_object.move(self.screen)

        # Check for collisions of spaceship with asteroids
        if self.spaceship:
            for asteroid in self.asteroids:
                if asteroid.collides_with(self.spaceship):
                    self.spaceship = None
                    self.message = "You lost!"
                    break

        # Check for collisions of bullets with asteroids
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if asteroid.collides_with(bullet):
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    asteroid.split()
                    break
        
        # Remove bullets which are off the screen
        for bullet in self.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.position):
                self.bullets.remove(bullet)

        if not self.asteroids and self.spaceship:
            self.message = "You won!"

    # Update the game drawing
    def _draw(self):
        self.screen.blit(self.background, (0, 0))
        for game_object in self._get_game_objects():
            game_object.draw(self.screen)

        if self.message:
            print_text(self.screen, self.message, self.font)
            
        pygame.display.flip()
        self.clock.tick(60) # Set the frame rate to 60 FPS

    # Helper method to get all the game objects
    def _get_game_objects(self):
        game_objects = [*self.asteroids, *self.bullets]
        if self.spaceship:
            game_objects.append(self.spaceship)
        return game_objects
