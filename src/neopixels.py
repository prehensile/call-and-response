import time
import board
import neopixel
import os
import random

from PIL import Image


IS_PI = os.uname()[4].startswith("arm")




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

if __name__ == "__main__":
    g = Glower()
    g.brightness = 255.0
    g.decay_mult = 0.9
    fps = 1.0 / 18.0
    while True:
        if random.random() > 0.99:
            g.brightness = 128.0
        g.tick()
        time.sleep( fps )