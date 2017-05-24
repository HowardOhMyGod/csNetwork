import socket
from packet import *
import time

RTT = 0.1

class Server:
    # create UDP server socket and bind port
    def __init__(self, port):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSocket.bind(('', port))
        self.port = port

    # ack logic
    def ackInc(self,seq):
        return seq + 1

    # start server
    def start(self):
        print 'Server listen on port: ' + str(self.port)

        while True:
            packet, address = self.serverSocket.recvfrom(1024)

            # correct checksum
            if chksum(packet) == 0:
                packet = Packet().unpack(packet)

                # make response packet
                resPacket = Packet()
                resPacket.ack = self.ackInc(packet[2])
                resPacket.dport = packet[1]

                time.sleep(RTT)
                self.serverSocket.sendto(resPacket.pack(), address)
            else:
                print chksum(packet)

if __name__ == "__main__":
    server = Server(12000)
    server.start()
