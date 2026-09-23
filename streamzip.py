"""Stream members out of a zip that was written with data descriptors, without random access."""
import struct, zlib


class Stream:
    def __init__(self, f, chunk=1 << 20):
        self.f, self.chunk, self.buf = f, chunk, b""

    def need(self, n):
        while len(self.buf) < n:
            c = self.f.read(self.chunk)
            if not c:
                return False
            self.buf += c
        return True

    def take(self, n):
        self.need(n); b, self.buf = self.buf[:n], self.buf[n:]; return b


def members(f, want=lambda name: True):
    """yield (name, bytes or None) for each member; bytes only if want(name)"""
    s = Stream(f)
    while s.need(30):
        sig, ver, flag, meth, t, dte, crc, cs, us, nl, el = struct.unpack("<IHHHHHIIIHH", s.buf[:30])
        if sig != 0x04034b50:
            return
        s.take(30); name = s.take(nl).decode(errors="replace"); s.take(el)
        keep = want(name); out = [] if keep else None
        if meth == 8:
            d = zlib.decompressobj(-15)
            while not d.eof:
                if not s.buf and not s.need(1):
                    return
                data = s.buf; s.buf = b""
                o = d.decompress(data)
                if keep: out.append(o)
                if d.eof:
                    s.buf = d.unused_data
        else:  # stored: sizes must be in the header
            data = s.take(cs)
            if keep: out.append(data)
        if flag & 8:  # data descriptor, optional signature
            s.need(4)
            if s.buf[:4] == b"PK\x07\x08": s.take(4)
            s.take(12)  # crc, csize, usize (zip32); zip64 would be 20
        yield name, (b"".join(out) if keep else None)
