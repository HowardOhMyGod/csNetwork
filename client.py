import socket
from packet import *
import time
from nat import NAT
from random import randint

BUFFER_SIZE = 10240
RTT = 0.1
THRES = 65535
MSS = 512


class Client:
    # create UDP client socket and bind port
    def __init__(self, src, sport):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSocket.bind((src, sport))

        self.sport = sport
        self.src = src

        # display parameters
        print '=====Parameter====='
        print 'The RTT delay = {} ms'.format(RTT*100*2)
        print 'The threshold = {} bytes'.format(THRES)
        print 'The MSS = {} bytes'.format(MSS)
        print 'The buffer size = {} bytes'.format(BUFFER_SIZE)
        print 'Client starts at {0} : {1}'.format(src, sport)
        print '==================='

        # input server IP:port
        print 'Please Input Server [IP] [Port] to connect'

        # _input = raw_input('>>> ').split(' ')
        _input = '192.0.0.3 45678'.split(' ')
        self.dst = _input[0]
        self.dport = int(_input[1])

    # three-way hand shake
    def threeway(self):
        print '=====Start the three-way handshake====='
        print 'Send a packet(SYN) to {0} : {1}'.format(self.dst, self.dport)

        # first connect pkt
        syn_pkt = Packet(self.sport, self.dport)
        syn_pkt.dst = self.dst
        syn_pkt.src = self.src
        syn_pkt.seq = randint(1, 10000)
        syn_pkt.SYN = 1

        print Packet().unpack(syn_pkt.pack())

    # send packet to server
    def send(self):
        # make packet and set RTT = 200ms
        pkt = self.makePkt()

        time.sleep(RTT)

        # send and recieve packet from server
        self.clientSocket.sendto(pkt, (self.dst, self.dport))
        self.recv()

    # recieve packet from server
    def recv(self):
        packet, server = self.clientSocket.recvfrom(BUFFER_SIZE)

        if chksum(packet) == 0:
            print Packet().unpack(packet)
            self.clientSocket.close()
        else:
            print chksum(packet)

if __name__ == "__main__":
    client = Client('127.0.0.3',2000)
    client.threeway()
