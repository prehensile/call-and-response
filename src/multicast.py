import socket
import struct
from http import client


class MulticastMessage( object ):
    def __init__( self, message, origin ):
        self.message = message
        self.origin = origin


# some defaults
MULTICAST_GROUP = "239.192.1.100"
MULTICAST_PORT = 5001
MULTICAST_TTL = 20
RECV_BUF_SIZE = 1024
BIND_ADDR = ''
BLOCK_RECV = False

class MulticastHandler( object ):
    

    def __init__( self, bind_addr=BIND_ADDR, multicast_group=MULTICAST_GROUP, multicast_port=MULTICAST_PORT, ttl=MULTICAST_TTL, buffer_size=RECV_BUF_SIZE, block_recv=BLOCK_RECV ):

        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        self.recv_buf_size = buffer_size

        self.socket_out = self.create_socket_out( ttl )
        self.socket_in = self.create_socket_in( bind_addr, multicast_group, multicast_port, ttl, block_recv )
        

    def packed_group( self, multicast_group ):
        return struct.pack("4sl", socket.inet_aton(multicast_group), socket.INADDR_ANY)
    

    def create_socket_out( self, ttl ):
        s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP )
        s.setsockopt( socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl )
        return s 
    

    def create_socket_in( self, bind_addr, multicast_group, multicast_port, ttl, blocking ):

        # cribbed from https://wiki.python.org/moin/UdpCommunication

        # Create the socket
        s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP )

        # Set some options to make it multicast-friendly
        s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        try:
            s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEPORT, 1 )
        except AttributeError:
            pass # Some systems don't support SO_REUSEPORT
        s.setsockopt( socket.SOL_IP, socket.IP_MULTICAST_TTL, ttl )
        s.setsockopt( socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1 )

        # Bind to the port
        s.bind( (bind_addr, multicast_port) )

        # Set some more multicast options
        # intf = socket.gethostbyname( socket.gethostname() )
        # s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(intf))

        s.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_ADD_MEMBERSHIP,
            self.packed_group( multicast_group )
        )

        # set blockingness of socket
        b = 1 if blocking else 0  # unsure if this is needed; translate True or False to 1 or 0
        s.setblocking( b )

        return s 
    

    def shutdown( self ):
        if self.socket_in:
            self.socket_in.setsockopt(
                socket.SOL_IP,
                socket.IP_DROP_MEMBERSHIP,
                #socket.inet_aton( MulticastHandler.MULTICAST_GROUP ) + socket.inet_aton('0.0.0.0')
                self.packed_group( self.multicast_group )
            )
            self.socket_in.close()
    

    def get_message( self ):
        if self.socket_in:
            try:
                data, sender_addr = self.socket_in.recvfrom( self.recv_buf_size )
                return MulticastMessage( data, sender_addr )
            except BlockingIOError:
                # let blocking errors go, since we don't care if there's no data
                pass


    def send_message( self, message ):

        if type(message) != bytes:
            message = str.encode( message )

        self.socket_out.sendto(
            message,  #b"robot",
            ( self.multicast_group, self.multicast_port )
        )