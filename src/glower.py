import time
from PIL import Image


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


class GlowerColour( object ):
    
    def __init__( self, img_path ):
        
        grad_image:Image = Image.open( img_path )
        self.grad_image = grad_image.convert('RGB')

        self.time_decay_brightness = 10.0
        self.colour_decay = 0.99

        self.ts_pulse_began = 0.0

        self.brightness_factor = 0.0
        self.colour_factor = 0.1
        
        self.colour_grow = 1.2


    def current_colour( self ):
        
        px = (self.grad_image.width-1) * self.colour_factor
        py = (self.grad_image.height-1) * self.brightness_factor

        return self.grad_image.getpixel( (px,py) )
    

    def tick( self ):

        if self.ts_pulse_began > 0.0:
            
            pulse_elapsed = time.time() - self.ts_pulse_began
            # print( pulse_elapsed )
            if pulse_elapsed < self.time_decay_brightness:
                bf = self.lerp( pulse_elapsed, 1.0, -1.0, self.time_decay_brightness )
                bf = clamp( bf, 0.0, 1.0 )
                # print( "bf:", bf )
                self.brightness_factor = bf
            else:
                self.brightness_factor = 0.0

            cf = self.colour_factor * self.colour_decay
            self.colour_factor = min( cf, 1.0 )


    def pulse( self ):
        
        self.brightness_factor = 1.0
        
        #cf = self.colour_factor * self.colour_grow
        #self.colour_factor = min( cf, 1.0 )
        
        self.ts_pulse_began = time.time()
    

    def lerp( self, t, b, c, d ):
        # Penner's easeInOutQuad
        # see https://gist.github.com/th0ma5w/9883420
        t /= d/2
        if t < 1:
            return c/2*t*t + b
        t-=1
        return -c/2 * (t*(t-2) - 1) + b