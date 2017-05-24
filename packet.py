import struct

class Packet:
    def __init__(self, sport = 0, dport = 0):
        self.sport = sport
        self.dport = dport
        self.seq = 0
        self.ack = 0
        self.chksum = 0

        #  pseudo-header for checksum computation
        # self.src = 0
        # self.dst = 127.0.0.1


    def pack(self):
        packet = struct.pack('!2H2Ih', self.sport, self.dport, self.seq, self.ack, self.chksum)
        checksum = chksum(packet)

        return struct.pack('!2H2Ih', self.sport, self.dport, self.seq, self.ack, checksum)
    def unpack(self, packet):
        return struct.unpack('!2H2Ih', packet)


def chksum(pkt):
    def carry_around_add(a, b):
        c = a + b
        return (c & 0xffff) + (c >> 16)

    if len(pkt) % 2 != 0:
        pkt += '\0'

    s = 0
    for i in range(0, len(pkt), 2):
        w = (ord(pkt[i]) << 8 ) + ord(pkt[i+1])
        s = carry_around_add(s, w)
    return ~s & 0xfff
