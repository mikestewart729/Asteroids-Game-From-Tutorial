from pygame.math import Vector2 # Vectors for positions and velocities
from pygame.transform import rotozoom # Handle rotation of sprites

from utils import load_sprite, load_sound, wrap_position, get_random_velocity

UP = Vector2(0, -1)

# Generic game object class from which asteroids and ships will inherit
class GameObject:
    # Constructor
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position) # Store the position as a vector
        self.sprite = sprite # Sprite image of game object
        self.radius = sprite.get_width() / 2 # Radius = half of the bounding square
        self. velocity = Vector2(velocity) # Store velocity as a vector

    # Draw a GameObject to the surface
    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius) # Get upper left corner
        surface.blit(self.sprite, blit_position) # Draw sprite on the surface

    # Move a GameObject
    def move(self, surface):
        self.position = wrap_position(self.position + self.velocity, surface) # Move in direction of motion

    # Simple collision checking for GameObjects
    def collides_with(self, other_obj):
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius # Return true if radii overlap

# Spaceship class, which inherits from GameObject
class Spaceship(GameObject):
    # Class constants
    MANEUVERABILITY = 3
    ACCELERATION = 0.25
    BULLET_SPEED = 3
    SPEED_CAP = 4

    # Constructor utilizing the parent constructor
    def __init__(self, position, create_bullet_callback):
        # Create a callback for bullets
        self.create_bullet_callback = create_bullet_callback
        # Load the sound file for the lasers
        self.laser_sound = load_sound("laser")
        # Add a direction to the spaceship, make a copy of the constant UP
        self.direction = Vector2(UP)
        # Call to parent class constructor
        super().__init__(position, load_sprite("spaceship"), Vector2(0))

    # Method to rotate the ship
    def rotate(self, clockwise = True):
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)
    
    # Override the draw method
    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    # Accelerate the ship
    def accelerate(self):
        self.velocity += self.direction * self.ACCELERATION
        if self.velocity.length() > self.SPEED_CAP:
            self.velocity.scale_to_length(self.SPEED_CAP)

    # Shoot a bullet
    def shoot(self):
        bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
        bullet = Bullet(self.position, bullet_velocity)
        self.create_bullet_callback(bullet)
        self.laser_sound.play()

# Create a class to handle asteroid objects
class Asteroid(GameObject):
    # Constructor
    def __init__(self, position, create_asteroid_callback, size = 3):
        self.create_asteroid_callback = create_asteroid_callback
        self.size = size

        size_to_scale = {
            3: 1,
            2: 0.5,
            1: 0.25
        }

        scale = size_to_scale[size]
        sprite = rotozoom(load_sprite("asteroid"), 0, scale)

        super().__init__(position, sprite, get_random_velocity(1, 3)) 
    
    # Split the asteroid into smaller ones
    def split(self):
        if self.size > 1:
            for _ in range(2):
                asteroid = Asteroid(
                    self.position, self.create_asteroid_callback, self.size - 1
                )
                self.create_asteroid_callback(asteroid)

# Create a class for the bullets the ship fires
class Bullet(GameObject):
    # Constructor for bullet objects
    def __init__(self, position, velocity):
        super().__init__(position, load_sprite("bullet"), velocity)
    
    # Move a Bullet, overriding GameObject move
    def move(self, surface):
        self.position = self.position + self.velocity