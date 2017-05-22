import socket
from packet import *

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
        self.clientSocket.sendto(pkt, ('127.0.0.1', self.dport))

    # recieve packet from server
    def recv(self):
        packet, server = self.clientSocket.recvfrom(1024)
        print Packet().unpack(packet)
        self.clientSocket.close()

if __name__ == "__main__":
    client = Client(12000)
    client.send()
    client.recv()
