import os
import random
import time

import pygame
from PIL import Image

from glower import GlowerColour


IS_PI = os.uname()[4].startswith("arm")


class PixelDisplay( object ):

    def __init__( self ):
        self.glower = GlowerColour( "gradient.png" )

        self.pixels = None
        self.img_debug = None
        if IS_PI: 
            import board, neopixel
            self.pixels = neopixel.NeoPixel(board.D18, 12, pixel_order=neopixel.GRB)    
        else:
            pygame.init()
            self.pixels = pygame.display.set_mode((1024, 2048))
            self.img_debug = pygame.image.fromstring(
                self.glower.grad_image.tobytes(),
                self.glower.grad_image.size,
                self.glower.grad_image.mode
            )
        
        self.fill( (0,0,0) )


    def draw_debug( self ):
        
        self.pixels.blit(
            self.img_debug,
            self.img_debug.get_rect() )
        
        x = int(self.glower.colour_factor * self.glower.grad_image.width )
        y = int(self.glower.brightness_factor * self.glower.grad_image.height )
        cross_length = 10
        color = (255,0,0)
        pygame.draw.line(
            self.pixels,
            color,
            ( x, y - cross_length ),
            ( x, y + cross_length )
        )
        pygame.draw.line(
            self.pixels,
            color,
            ( x - cross_length, y ),
            ( x + cross_length, y )
        )
        
        pygame.display.flip()
        

    def fill( self, colour ):
        self.pixels.fill( colour )


    def tick( self ):
        
        self.glower.tick()
        
        c = self.glower.current_colour()
        self.fill( c )
        
        if not IS_PI:
            self.draw_debug()
    

    def pulse( self ):
        self.glower.pulse()


##
## MOST STUFF FROM HERE DOWN IS NONSENSE
##

class Glower( object ):

    def __init__( self ):
        self.brightness = 0
        self.decay_mult = 0.8
        self.neopixels = neopixel.NeoPixel(board.D18, 12, pixel_order=neopixel.GRB,auto_write=False)
        self.neopixels.fill((0,0,0))
        self.neopixels.show


    def tick( self ):
        
        if self.brightness > 0.0:
            self.brightness *= self.decay_mult

        self.neopixels.fill((self.brightness,self.brightness,self.brightness))
        self.neopixels.show()


def gradient_anim():

    neopixels = None
    if IS_PI: 
        import board, neopixel
        neopixels = neopixel.NeoPixel(board.D18, 12, pixel_order=neopixel.GRB,auto_write=False)
        neopixels.fill((0,0,0))
        neopixels.show()

    grad_image:Image = Image.open( "gradient.png" )
    grad_image = grad_image.convert('RGB')

    try:

        fps = 1.0 / 30.0 
        grad_direction = 1.0
        grad_pos = 0

        while True:

            r,g,b = grad_image.getpixel((grad_pos,0))
            print( (r,g,b) )
            if IS_PI:
                neopixels.fill( (r,g,b) )
                neopixels.show()

            grad_pos += grad_direction
            if grad_pos >= grad_image.width:
                grad_pos = 0 

            time.sleep( fps )

    except KeyboardInterrupt:
        pass

    if IS_PI:
        neopixels.fill((0,0,0))
        neopixels.show()

    
def animate_glower():
    g = Glower()
    g.brightness = 255.0
    g.decay_mult = 0.9
    fps = 1.0 / 18.0
    while True:
        if random.random() > 0.99:
            g.brightness = 128.0
        g.tick()
        time.sleep( fps )


def animate_glowercolour():
    import glower
    g = glower.GlowerColour( "gradient.png" )

    pixels = None
    img = None
    if IS_PI: 
        import board, neopixel
        pixels = neopixel.NeoPixel(board.D18, 12, pixel_order=neopixel.GRB)    
    else:
        import pygame
        pygame.init()
        pixels = pygame.display.set_mode((1024, 2048))
        img = pygame.image.fromstring(
            g.grad_image.tobytes(),
            g.grad_image.size,
            g.grad_image.mode
        )
    pixels.fill( (0,0,0) )

    fps = 1.0 / 18.0
    while True:
        
        if random.random() > 0.9:
            g.pulse()
        
        g.tick()
        
        c = g.current_colour()
        pixels.fill( c )
        if not IS_PI:
            r = img.get_rect()
            pixels.blit( img, r )
            
            x = int(g.colour_factor * g.grad_image.width )
            y = int(g.brightness_factor * g.grad_image.height )
            cross_length = 10
            color = (255,0,0)
            pygame.draw.line(
                pixels,
                color,
                ( x, y - cross_length ),
                ( x, y + cross_length )
            )
            pygame.draw.line(
                pixels,
                color,
                ( x - cross_length, y ),
                ( x + cross_length, y )
            )
            
            pygame.display.flip()
        
        time.sleep( fps )


if __name__ == "__main__":
    # animate_glower()
    animate_glowercolour()