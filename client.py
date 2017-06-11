import socket
from packet import *
import time
from nat import NAT
from random import randint
from sys import exit

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

        # track seq_num
        self.seq = 0

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
        _input = '127.0.0.1 12000'.split(' ')
        self.dst = _input[0]
        self.dport = int(_input[1])

    # three-way hand shake
    def threeway(self):
        print '=====Start the three-way handshake====='
        self.seq = randint(1, 10000)
        # first connect pkt
        syn_pkt = Packet(self.sport, self.dport)
        syn_pkt.dst = self.dst
        syn_pkt.src = self.src
        syn_pkt.seq = self.seq
        syn_pkt.SYN = 1
        # print 'seq = ', syn_pkt.seq

        print 'Send a packet(SYN) to {0} : {1}'.format(self.dst, self.dport)
        self.send(syn_pkt.pack(), self.dst, self.dport)

        # waiting for server accept
        while True:
            packet, serv_addr = self.clientSocket.recvfrom(BUFFER_SIZE)
            rcv_pkt = Packet().unpack(packet)

            print 'Receive a packet(SYN/ACK) from {0}'.format(serv_addr)
            print '     Receive a packet (seq_num = {0}, ack_num = {1})'.format(rcv_pkt[2], rcv_pkt[3])

            # synbit == ackbit == 1 and ack_num == seq_num + 1
            if rcv_pkt[5] == rcv_pkt[6] == 1 and rcv_pkt[3] == (self.seq + 1):
                syn_pkt = Packet(self.sport, self.dport)
                syn_pkt.dst = self.dst
                syn_pkt.src = self.src
                syn_pkt.ack = rcv_pkt[2] + 1
                syn_pkt.ACK = 1
                syn_pkt.seq = rcv_pkt[3]

                print 'Send a packet(SYN) to {0} : {1}'.format(rcv_pkt[7], rcv_pkt[0])
                self.send(syn_pkt.pack(), rcv_pkt[7], rcv_pkt[0])
                print '=====Complete the three-way handshake====='
                break
            else:
                print 'Three-way handshake failed...'
                exit()
    # send packet to server
    def send(self, pkt, dst, dport):
        time.sleep(RTT)
        # send and recieve packet from server
        self.clientSocket.sendto(pkt, (dst, dport))

    # recieve packet from server
    def startTorecv(self):
        ack = 0

        print 'Receive a file from {} : {}'.format(self.dst, self.dport)
        while ack != 10240:
            packet, server = self.clientSocket.recvfrom(BUFFER_SIZE)
            pkt = Packet().unpack(packet, plen = MSS)
            correct = chksum(packet)

            ack = pkt[2] + MSS

            if correct == 0:
                print recv_msg(pkt)

                reply = Packet(self.sport, self.dport)
                reply.seq = pkt[3]
                reply.ack = ack
                reply.dst = self.dst
                reply.src = self.src

                self.send(reply.pack(), self.dst, self.dport)
            else:
                print 'Receive fail...',chksum(packet)
    # def fourway(self):
    #     self.clientSocket.close()




def recv_msg(pkt):
    return '          Receive a packet (seq_num = {0}, ack_num = {1})'.format(pkt[2], pkt[3])


if __name__ == "__main__":
    client = Client('127.0.0.3',2000)
    client.threeway()
    client.startTorecv()
