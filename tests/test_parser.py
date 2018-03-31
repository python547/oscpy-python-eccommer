from oscpy.parser import parse, padded, read_message
import struct


def test_parse_int():
    assert parse(b'i', struct.pack('>i', 1))[0] == 1


def test_parse_float():
    assert parse(b'f', struct.pack('>f', 1.5))[0] == 1.5


def test_padd_string():
    for i in range(8):
        length = padded(i)
        assert length % 4 == 0
        assert length >= i


def test_parse_string():
    assert parse(b's', struct.pack('%is' % padded(len('t')), b't'))[0] == b't'
    s = b'test'
    assert parse(b's', struct.pack('%is' % len(s), s))[0] == s
    s = b'test padding'
    assert parse(b's', struct.pack('%is' % padded(len(s)), s))[0] == s


def test_parse_blob():
    l = 10
    data = tuple(range(l))
    pad = padded(l, 8)
    fmt = '>i%iQ' % pad
    s = struct.pack(fmt, l, *(data + (pad - l) * (0, )))
    result = parse(b'b', s)[0]
    assert result == data


def test_read_message():
    address = b'/test'
    pad = padded(len(address))
    tags = b'i'
    pad_tags = padded(len(tags))
    values = [1]

    fmt = b'>%isc%is%ii' % (pad, pad_tags, len(values))
    assert read_message(
        struct.pack(
            fmt, address, b',', tags, *values)
    ) == (address, tags, values)
