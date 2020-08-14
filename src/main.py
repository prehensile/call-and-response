import json
import logging
import random
import time

import pygame

import multicast
import glower
import neopixels
import shortuuid


class StateMachine( object ):
        
    STATE_NONE = "none"
    STATE_IDLE = "idle"
    STATE_LISTENING = "listening"
    STATE_VIBING = "vibing"
    STATE_RINGING = "ringing"
    STATE_RESTING = "resting"
    
    def __init__( self ):
        self.state = StateMachine.STATE_NONE
        self.ts_state_began = None
        self.previous_state = None
        self.change_flag = False
    
    def set_state( self, state ):
        print( "set state:", state )
        if state != self.state:
            self.previous_state = self.state
            self.state = state
            self.change_flag = True
            self.ts_state_began = time.time()
    
    def state_time( self ):
        if self.ts_state_began:
            return time.time() - self.ts_state_began
    
    def did_change( self ):
        c = self.change_flag
        self.change_flag = False
        return c


# set up some instances of things
pygame.init()
states = StateMachine()
network = multicast.MulticastHandler()

pixels = neopixels.PixelDisplay()
pixels.brightness_decay = 0.999

# load sounds
fn_sounds = [ "01.wav", "02.wav", "03.wav", "04.wav" ]
sounds = []
for fn_sound in fn_sounds:
    sound = pygame.mixer.Sound( "audio/bowls/" + fn_sound )
    sounds.append( sound )


# some config
listen_time  = 4.0
min_rest_length = listen_time
max_rest_length = 12.0
reply_chance = 0.6
vibe_count = 0


try:
    
    do_runloop = True
    last_sound = None
    current_channel = None
    current_rest_length = 0
    current_vibe_interval = 0
    client_id = "%s" % shortuuid.uuid()
    update_interval = 1.0 / 18.0

    
    def play_bell( index=None ):
        global last_sound

        # sound = None
        # if index is not None:
        #     sound = sounds[ index ]
        # else:
        #     # choose a bell
        #     while True:
        #         sound = random.choice( sounds )
        #         if sound != last_sound:
        #             break
        # 

        sound = sounds[ index ] 
        
        # play a bell sound
        last_sound = sound
        return sound.play(), sound

    
    states.set_state( states.STATE_RINGING )

    while do_runloop:
        
        now = time.time()

        pixels.tick()
        
        if states.state == states.STATE_RINGING:
            
            # ring a bell
            # index = None if (states.previous_state == StateMachine.STATE_VIBING) else 0
            current_channel, sound = play_bell( vibe_count )

            # tell other instances what we're playing
            message = json.dumps( {
                "chime" :  sounds.index(sound),
                "client-id" : client_id,
                "message-id" : shortuuid.uuid()
            } )
            network.send_message( message )

            # pretty lights!
            pixels.pulse()

            # set next state
            states.set_state( states.STATE_LISTENING )


        elif states.state == states.STATE_LISTENING:
             # happens for a little time after ringing. 
             # wait to see if someone else is ringing a bell

            if (states.state_time() < listen_time) and ( vibe_count<len(sounds) ):
                # check incoming network messages

                msg = network.get_message()

                if msg is not None:

                    j = json.loads( msg.message )

                    if j["client-id"] != client_id:
                        
                        print( "message received: ", msg.message, msg.origin )
                        
                        if random.random() < reply_chance:
                            # this is a message from someone else
                            print( "... vibe to message with id:", j["message-id"])

                            # set repeat time to the amount of time it took someone else to reply to us
                            # current_vibe_interval = states.state_time() + (random.random() * listen_time)
                            current_vibe_interval =  0.2 + (random.random() * (listen_time*0.2))

                            # move to vibing state
                            vibe_count += 1
                            states.set_state( states.STATE_VIBING )

            else:
                # no-one has made another sound during listening time, move to resting state
                states.set_state( states.STATE_RESTING )
        

        elif states.state == states.STATE_VIBING:

            # wait for the vibe interval...
            if states.state_time() >= current_vibe_interval:
                # then ring again
                states.set_state( states.STATE_RINGING )


        elif states.state == states.STATE_RESTING:

            if states.did_change():
                # we are coming in to a new state
                current_rest_length = min_rest_length + ( random.random() * (max_rest_length-min_rest_length) )
                vibe_count = 0

            # resting state, do nothing for a while
            if states.state_time() >= current_rest_length:
                # then ring again
                states.set_state( states.STATE_RINGING )
        
        
        time.sleep( update_interval )

except KeyboardInterrupt as e:
    pass

except Exception as e:
    logging.exception( e )
    
print( "Shutting down...")
network.shutdown()
pygame.quit()
