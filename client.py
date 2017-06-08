import socket
from packet import *
import time
from nat import NAT
from random import randint

BUFFER_SIZE = 10240
RTT = 0.1
THRES = 65535
MSS = 512
BUFFER = 10240

class Client:
    # create UDP client socket and bind port
    def __init__(self, src, sport):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSocket.bind((src, sport))

        self.sport = sport
        self.src = src

        # parameter
        print '=====Parameter====='
        print 'The RTT delay = ' + str(100*2*RTT) + ' ms'
        print 'The threshold = ' + str(THRES) +' bytes'
        print 'The MSS = ' + str(MSS) + ' bytes'
        print 'The buffer size = ' + str(BUFFER) + ' bytes'
        print 'Client Start at', src, sport
        print '==================='

        # input connect server
        # print 'Please input server [ip] [port] to connect :'
        # _input = raw_input('>>>').split(' ')
        _input = '127.0.0.1 564'.split(' ')

        self.dst = _input[0]
        self.dport = int(_input[1])

    # three-way handshake send to client
    def handshake(self):
        print '=====Start the three-way handshake====='
        print 'Send a packet(SYN) to {0} : {1}'.format(self.dst, self.dport)

        syn_pkt = Packet(self.sport, self.dport)

        # initial random seq num and syn bit
        syn_pkt.seq = randint(1, 10000)
        syn_pkt.SYN = 1
        syn_pkt.src = self.src
        syn_pkt.dst = self.dst

        syn_pkt = syn_pkt.pack()


    # send packet to server
    def send(self, pkt):
        time.sleep(RTT)

        # send and recieve packet from server
        self.clientSocket.sendto(pkt, (self.dst, self.dport))

    # recieve packet from server
    def recv(self):
        packet, server = self.clientSocket.recvfrom(BUFFER_SIZE)

        if chksum(packet) == 0:
            print Packet().unpack(packet)
            self.clientSocket.close()
        else:
            print chksum(packet)

if __name__ == "__main__":
    client = Client('127.0.0.3', 2000)
    client.handshake()
