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
        self.dst = ''
        self.dport = 0

        # track seq
        self.seq = 0

        # send file
        self.file = Packet().makeData()

        # flow control and congestion control
        self.cwnd = 1
        self.rwnd = BUFFER_SIZE

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

            self.dst = address[0]
            self.dport = address[1]

            pkt = Packet().unpack(packet)
            # first receive client ack = 0 synbit = 1
            if pkt[5] == 0 and pkt[6] == 1:
                print '=====Start the three-way handshake====='
                print 'Receive a packet(SYN) from {0}'.format(address)
                print '     Recieve a packet (seq_num = {0}, ack_num = {1})'.format(pkt[2], pkt[3])

                self.seq = randint(1, 10000)
                reply_pkt = self.pkt_init()
                reply_pkt.ack = pkt[2] + 1
                reply_pkt.seq = self.seq
                reply_pkt.SYN = 1
                reply_pkt.ACK = 1

                print 'Send a packet(SYN/ACK) to {0} : {1}'.format(pkt[8], pkt[0])
                self.send(reply_pkt.pack(), pkt[8], pkt[0])

            # second receive ackbit = 1
            elif pkt[5] == 1 and pkt[3] == (self.seq + 1):
                self.ack = pkt[2] + 1
                print 'Recieve a packet(ACK) from {}'.format(address)
                print '     Recieve a packet (seq_num = {0}, ack_num = {1})'.format(pkt[2], pkt[3])
                print '=====Complete the three-way handshake====='
                break
            else:
                print 'Three-way handshake failed...'
                exit()
    # send file to client after three-way connection
    def startTosend(self):
        print '\nStart to send the file, the file size is 10240 bytes.'
        print '*****Slow start*****'

        self.seq = 0
        self.cwnd = MSS

        base = 1
        next_seq = 0

        # send segment until file transmit completly
        while next_seq < len(self.file):
            print 'cwnd = {0}, rwnd = {1}, threshold = {2}'.format(self.cwnd, self.rwnd, THRES)

            reply_pkt = self.pkt_init()

            reply_pkt.ack = self.ack
            reply_pkt.seq = self.seq

            data = self.file[next_seq: next_seq + MSS]
            # print 'data len = {0}, next_seq = {1}'.format(len(data), next_seq)
            print '          Send a packet at : {} byte'.format(next_seq + 1)
            self.send(reply_pkt.pack(data = data), self.dst, self.dport)

            while True:
                packet, address = self.serverSocket.recvfrom(1024)
                pkt = Packet().unpack(packet)

                if pkt[3] == self.seq + MSS:
                    print recv_msg(pkt)
                    next_seq = pkt[3]
                    self.ack = pkt[2] + 1
                    self.seq = next_seq
                    break
                else:
                    print 'Server stop transmisstin...'
                    break
    # close a connection
    def fourway(self):
        print '=====Start the four-way handshake====='
        pkt = self.pkt_init()
        pkt.FIN = 1
        pkt.seq = self.seq
        pkt.ack = self.ack

        print 'Send a packet(FIN) to {0} : {1}'.format(self.dst, self.dport)
        self.send(pkt.pack(), self.dst, self.dport)

        while True:
            packet, address = self.serverSocket.recvfrom(1024)
            rcv_pkt = Packet().unpack(packet)

            # second handshake
            if rcv_pkt[5] == 1 and rcv_pkt[3] == self.seq + 1:
                print 'Receive a packet(ACK) from ', address
                print recv_msg(rcv_pkt)
            # third handshake
            elif rcv_pkt[7] == 1:
                print 'Receive a packet(FIN) from ', address
                print recv_msg(rcv_pkt)
                print 'Send a packet(ACK) to {0} : {1}'.format(self.dst, self.dport)

                pkt = self.pkt_init()
                pkt.ACK = 1
                pkt.ack = rcv_pkt[2] + 1
                pkt.seq = rcv_pkt[3]

                self.send(pkt.pack(), self.dst, self.dport)
                # self.serverSocket.close()
                print '=====Complete the four-way handshake====='
                print 'Listening for Node...'
                break

    def pkt_init(self):
        pkt = Packet(self.port, self.dport)
        pkt.dst = self.dst
        pkt.src = self.ip

        return pkt

    def send(self, pkt, dst, dport):
        time.sleep(RTT)
        self.serverSocket.sendto(pkt, (dst, dport))

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

def recv_msg(pkt):
    return '          Receive a packet (seq_num = {0}, ack_num = {1})'.format(pkt[2], pkt[3])

if __name__ == "__main__":
    server = Server('127.0.0.1', 12000)
    server.threeway()
    server.startTosend()
    server.fourway()
