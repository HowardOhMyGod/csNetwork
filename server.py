import socket
from packet import *
import time
from random import randint
from sys import exit

BUFFER_SIZE = 10240
RTT = 0.1
THRES = 65535
MSS = 512

class Server:
    # create UDP server socket and bind port
    def __init__(self, ip, port):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSocket.bind((ip, port))
        self.port = port
        self.ip = ip

        # track seq
        self.seq = 0

        # display parameters
        print '=====Parameter====='
        print 'The RTT delay = {} ms'.format(RTT*100*2)
        print 'The threshold = {} bytes'.format(THRES)
        print 'The MSS = {} bytes'.format(MSS)
        print 'The buffer size = {} bytes'.format(BUFFER_SIZE)
        print 'Server starts at {0} : {1}'.format(ip, port)
        print '==================='
    # three-way handshake with client
    def threeway(self):
        while True:
            packet, address = self.serverSocket.recvfrom(1024)
            print '=====Start the three-way handshake====='
            print 'Receive a packet(SYN) from {0}'.format(address)

            pkt = Packet().unpack(packet)
            # first receive client ack = 0 synbit = 1
            if pkt[5] == 0 and pkt[6] == 1:
                print '     Recieve a packet (seq_num = {0}, ack_num = {1})'.format(pkt[2], pkt[3])

                self.seq = randint(1, 10000)
                reply_pkt = Packet(self.port, address[1])
                reply_pkt.ack = pkt[2] + 1
                reply_pkt.seq = self.seq
                reply_pkt.SYN = 1
                reply_pkt.ACK = 1
                reply_pkt.src = self.ip
                reply_pkt.dst = address[0]

                print 'Send a packet(SYN/ACK) to {0} : {1}'.format(pkt[7], pkt[0])
                self.send(reply_pkt.pack(), pkt[7], pkt[0])

            # second receive ackbit = 1
            elif pkt[5] == 1 and pkt[3] == (self.seq + 1):
                print '     Recieve a packet (seq_num = {0}, ack_num = {1})'.format(pkt[2], pkt[3])
                print '=====Complete the three-way handshake====='
                break
            else:
                print 'Three-way handshake failed...'
                exit()
    def send(self, pkt, dst, dport):
        time.sleep(RTT)
        self.serverSocket.sendto(pkt, (dst, dport))

    # ack logic
    def ackInc(self,seq):
        return seq + 1

    # server receive
    def recv(self):
        while True:
            packet, address = self.serverSocket.recvfrom(1024)
            # correct checksum
            if chksum(packet) == 0:
                packet = Packet().unpack(packet)

                # make response packet
                resPacket = Packet(address[1], packet[1])
                resPacket.ack = self.ackInc(packet[2])
                resPacket.src =  self.ip
                resPacket.dst = address[0]

                time.sleep(RTT)
                self.serverSocket.sendto(resPacket.pack(), address)
            else:
                print chksum(packet)

if __name__ == "__main__":
    server = Server('127.0.0.1', 12000)
    server.threeway()
