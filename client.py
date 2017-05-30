import socket
from packet import *
import time

BUFFER_SIZE = 10240
RTT = 0.1

class Client:
    # create UDP client socket and bind port
    def __init__(self, sport, dport):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSocket.bind(('127.0.0.1', sport))

        print 'Client Start at port: ', sport
        self.dport = dport
        self.sport = sport

    # make packet
    def makePkt(self):
        return Packet(self.sport, self.dport).pack()

    # send packet to server
    def send(self):
        # make packet and set RTT = 200ms
        pkt = self.makePkt()
        time.sleep(RTT)

        # send and recieve packet from server
        self.clientSocket.sendto(pkt, ('127.0.0.1', self.dport))
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
    client = Client(2000, 12000)
    client.send()
