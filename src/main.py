import json
import logging
import random
import time
import uuid

import pygame

import multicast


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
    
    def set_state( self, state ):
        print( "set state:", state )
        if state != self.state:
            self.previous_state = self.state
            self.state = state
            self.ts_state_began = time.time()
    
    def state_time( self ):
        if self.ts_state_began:
            return time.time() - self.ts_state_began


pygame.init()
states = StateMachine()
network = multicast.MulticastHandler()


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


try:
    
    do_runloop = True
    last_sound = None
    current_channel = None
    current_rest_length = 0
    current_vibe_interval = 0
    client_id = "%s" % uuid.uuid4()

    
    def play_bell( index=None ):
        global last_sound

        sound = None
        if index is not None:
            sound = sounds[ index ]
        else:
            # choose a bell
            while True:
                sound = random.choice( sounds )
                if sound != last_sound:
                    break 
        
        # play a bell sound
        last_sound = sound
        return sound.play(), sound

    
    states.set_state( states.STATE_RINGING )

    while do_runloop:
        
        now = time.time()
        
        if states.state == states.STATE_RINGING:
            
            # ring a bell
            index = None if (states.previous_state == StateMachine.STATE_VIBING) else 0
            current_channel, sound = play_bell( index )

            # tell other instances what we're playing
            message = json.dumps( { "chime" :  sounds.index(sound), "client-id" : client_id } )
            network.send_message( message )

            # set next state
            states.set_state( states.STATE_LISTENING )


        elif states.state == states.STATE_LISTENING:
             # happens for a little time after ringing. 
             # wait to see if someone else is ringing a bell

            if states.state_time() < listen_time:
                # check incoming network messages
                msg = network.get_message()
                if msg is not None:
                    print( "message received: ", msg.message, msg.origin )
                    j = json.loads( msg.message )

                    if j["client-id"] != client_id and ( random.random() < reply_chance ):
                        # this is a message from someone else
                        print( "... reply to this message")

                        # set repeat time to the amount of time it took someone else to reply to us
                        # current_vibe_interval = states.state_time() + (random.random() * listen_time)
                        current_vibe_interval =  0.2 + (random.random() * (listen_time/2))

                        # move to vibing state
                        states.set_state( states.STATE_VIBING )
                pass

            else:
                # no-one has made another sound during listening time, move to resting state
                current_rest_length = min_rest_length + ( random.random() * (max_rest_length-min_rest_length) )
                states.set_state( states.STATE_RESTING )
        

        elif states.state == states.STATE_VIBING:
            
            # wait for the vibe interval...
            if states.state_time() >= current_vibe_interval:
                # then ring again
                states.set_state( states.STATE_RINGING )


        elif states.state == states.STATE_RESTING:
            # resting state, do nothing for a while
            if states.state_time() >= current_rest_length:
                # then ring again
                states.set_state( states.STATE_RINGING )
        
        
        time.sleep( 0.1 )

except KeyboardInterrupt as e:
    pass

except Exception as e:
    logging.exception( e )
    
print( "Shutting down...")
network.shutdown()
pygame.quit()
