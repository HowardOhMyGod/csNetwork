import socket
from packet import *
import time
from random import randint
from sys import exit

BUFFER_SIZE = 10240
RTT = 0.1
THRES = 65535
MSS = 512

ROUTER = ('127.0.0.8', 1500)


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
    def recvfromServ(self):
        packet, addr = self.clientSocket.recvfrom(BUFFER_SIZE)

        return packet, addr

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
            packet, serv_addr = self.recvfromServ()
            rcv_pkt = Packet().unpack(packet)

            print 'Receive a packet(SYN/ACK) from {0} : {1}'.format(rcv_pkt[9], rcv_pkt[0])
            print '     Receive a packet (seq_num = {0}, ack_num = {1})'.format(rcv_pkt[2], rcv_pkt[3])

            # synbit == ackbit == 1 and ack_num == seq_num + 1
            if rcv_pkt[5] == rcv_pkt[6] == 1 and rcv_pkt[3] == (self.seq + 1):
                syn_pkt = Packet(self.sport, self.dport)
                syn_pkt.dst = self.dst
                syn_pkt.src = self.src
                syn_pkt.ack = rcv_pkt[2] + 1
                syn_pkt.ACK = 1
                syn_pkt.seq = rcv_pkt[3]

                print 'Send a packet(SYN) to {0} : {1}'.format(rcv_pkt[9], rcv_pkt[0])
                self.send(syn_pkt.pack(), rcv_pkt[9], rcv_pkt[0])
                print '=====Complete the three-way handshake====='
                break
            else:
                print 'Three-way handshake failed...'
                exit()
    # send packet to server
    def send(self, pkt, dst, dport):
        time.sleep(RTT)
        self.clientSocket.sendto(pkt, ROUTER)

    # recieve packet from server
    def startTorecv(self):
        ack = 0

        print 'Receive a file from {} : {}'.format(self.dst, self.dport)
        while ack != 10240:
            packet, server = self.recvfromServ()
            pkt = Packet().unpack(packet, plen = MSS)
            correct = chksum(packet)

            ack = pkt[2] + MSS

            if correct == 0:
                print recv_msg(pkt)

                reply = Packet(self.sport, self.dport)
                self.seq = pkt[3]
                reply.seq = self.seq
                reply.ack = ack
                reply.dst = self.dst
                reply.src = self.src
                reply.rwnd -= (pkt[2] + 1)

                self.send(reply.pack(), self.dst, self.dport)
            else:
                print 'Receive fail...',chksum(packet)
    def fourway(self):
        print '=====Start the four-way handshake'

        while True:
            packet, address = self.recvfromServ()
            rcv_pkt = Packet().unpack(packet)

            if rcv_pkt[7]:
                print 'Receive a packet(FIN) from {0} : {1}'.format(rcv_pkt[9], rcv_pkt[0])
                print recv_msg(rcv_pkt)

                pkt = Packet(self.sport, self.dport)
                pkt.dst = self.dst
                pkt.src = self.src
                pkt.seq = rcv_pkt[3]
                pkt.ACK = 1
                pkt.ack = rcv_pkt[2] + 1

                print 'Send a packet(ACK) to {0} : {1}'.format(rcv_pkt[9], rcv_pkt[0])
                self.send(pkt.pack(), self.dst, self.dport)

                pkt = Packet(self.sport, self.dport)
                pkt.dst = self.dst
                pkt.src = self.src
                seq = rcv_pkt[3]
                pkt.seq = seq
                pkt.FIN = 1
                pkt.ack = rcv_pkt[2] + 1



                print 'Send a packet(FIN) to {0} : {1}'.format(rcv_pkt[9], rcv_pkt[0])
                self.send(pkt.pack(), self.dst, self.dport)
            elif rcv_pkt[5] and rcv_pkt[3] == seq +1:
                print 'Receive a packet(ACK) from {0} : {1}'.format(rcv_pkt[9], rcv_pkt[0])
                print recv_msg(rcv_pkt)
                print '=====Complete the four-way handshake====='
                self.clientSocket.close()
                break




def recv_msg(pkt):
    return '          Receive a packet (seq_num = {0}, ack_num = {1})'.format(pkt[2], pkt[3])


if __name__ == "__main__":
    client = Client('127.0.0.3',2000)
    client.threeway()
    client.startTorecv()
    client.fourway()
