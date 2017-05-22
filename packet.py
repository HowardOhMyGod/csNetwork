import struct

class Packet:
    def __init__(self, sport = 0, dport = 0):
        self.sport = sport
        self.dport = dport
        self.seq = 0
        self.ack = 0
        self.chksum = 0

    def pack(self):
        return struct.pack('2H2Ih', self.sport, self.dport, self.seq, self.ack, self.chksum)

    def unpack(self, packet):
        return struct.unpack('2H2Ih', packet)
