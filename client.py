import socket
from packet import *
import time
from nat import NAT

BUFFER_SIZE = 10240
RTT = 0.1

class Client:
    # create UDP client socket and bind port
    def __init__(self, src, dst, sport, dport):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSocket.bind((src, sport))

        print 'Client Start at port: ', sport
        self.dport = dport
        self.sport = sport

        self.dst = dst
        self.src = src

    # make packet
    def makePkt(self):
        pkt = Packet(self.sport, self.dport)
        pkt.dst = socket.inet_pton(socket.AF_INET, self.dst)
        pkt.src = socket.inet_pton(socket.AF_INET, self.src)

        return pkt.pack()

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
    client = Client('127.0.0.3', '127.0.0.1', 2000, 12000)
    client.send()
