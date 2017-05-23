import socket
from packet import *
import time

BUFFER_SIZE = 10240
RTT = 0.1

class Client:
    # create UDP client socket and bind port
    def __init__(self, dport):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sport = self.clientSocket.getsockname()[1]
        self.dport = dport

    # make packet
    def makePkt(self):
        return Packet(self.sport, self.dport).pack()

    # send packet to server
    def send(self):
        pkt = self.makePkt()
        self.stime = time.time()
        time.sleep(RTT)
        self.clientSocket.sendto(pkt, ('127.0.0.1', self.dport))

    # recieve packet from server
    def recv(self):
        packet, server = self.clientSocket.recvfrom(BUFFER_SIZE)
        print Packet().unpack(packet)
        self.etime = time.time()
        print 'RTT : ', self.etime - self.stime
        self.clientSocket.close()

if __name__ == "__main__":
    client = Client(12000)
    client.send()
    client.recv()
