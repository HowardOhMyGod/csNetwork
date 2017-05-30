import struct


class Packet:
    def __init__(self, sport = 0, dport = 0):
        # TCP packet
        self.sport = sport
        self.dport = dport
        self.seq = 0
        self.ack = 0
        self.chksum = 0

        # IP packet
        self.dst = 0
        self.src = 0

    # pack tcp and ip packet
    def pack(self):
        tcp_packet = struct.pack('!2H2Ih', self.sport, self.dport, self.seq, self.ack, self.chksum)
        ip_pkt = struct.pack('!4s4s', self.src, self.dst)
        
        checksum = chksum(tcp_packet + ip_pkt)

        return struct.pack('!2H2Ih', self.sport, self.dport, self.seq, self.ack, checksum) + ip_pkt

    def unpack(self, packet):
        return struct.unpack('!2H2Ih4s4s', packet)


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

if __name__ == "__main__":
    pass
