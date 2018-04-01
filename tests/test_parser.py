from oscpy.parser import (
    parse, padded, read_message, read_bundle, format_message
)
from pytest import approx
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
    # XXX should we need to add the null byte ourselves?
    assert parse(
        b's', struct.pack('%is' % padded(len(s) + 1), s + b'\0')
    )[0] == s


def test_parse_blob():
    length = 10
    data = tuple(range(length))
    pad = padded(length, 8)
    fmt = '>i%iQ' % pad
    s = struct.pack(fmt, length, *(data + (pad - length) * (0, )))
    result = parse(b'b', s)[0]
    assert result == data


def test_read_message():
# example messages from
# http://opensoundcontrol.org/spec-1_0-examples#argument

    message_1 = (
        (b'/oscillator/4/frequency', [approx(440.0)]),
        [
            0x2f, 0x6f, 0x73, 0x63,
            0x69, 0x6c, 0x6c, 0x61,
            0x74, 0x6f, 0x72, 0x2f,
            0x34, 0x2f, 0x66, 0x72,
            0x65, 0x71, 0x75, 0x65,
            0x6e, 0x63, 0x79, 0x0,
            0x2c, 0x66, 0x0,  0x0,
            0x43, 0xdc, 0x0,  0x0,
        ]
    )

    message_2 = (
        (b'/foo', [1000, -1, b'hello', approx(1.234), approx(5.678)]),
        [
            0x2f, 0x66, 0x6f, 0x6f,
            0x0,  0x0,  0x0,  0x0,
            0x2c, 0x69, 0x69, 0x73,
            0x66, 0x66, 0x0,  0x0,
            0x0,  0x0,  0x3,  0xe8,
            0xff, 0xff, 0xff, 0xff,
            0x68, 0x65, 0x6c, 0x6c,
            0x6f, 0x0,  0x0,  0x0,
            0x3f, 0x9d, 0xf3, 0xb6,
            0x40, 0xb5, 0xb2, 0x2d,
        ]
    )

    source, msg = message_1
    msg = struct.pack('>%iB' % len(msg), *msg)
    address, tags, values, size = read_message(msg)
    assert address == source[0]
    assert values == source[1]

    source, msg = message_2
    msg = struct.pack('>%iB' % len(msg), *msg)
    address, tags, values, size = read_message(msg)
    assert address == source[0]
    assert tags == b'iisff'
    assert values == source[1]


def test_read_bundle():
    pad = padded(len('#bundle'))
    data = struct.pack('>%isQ' % pad, b'#bundle', 1)

    message_1 = (
        (b'/oscillator/4/frequency', [approx(440.0)]),
        [
            0x2f, 0x6f, 0x73, 0x63,
            0x69, 0x6c, 0x6c, 0x61,
            0x74, 0x6f, 0x72, 0x2f,
            0x34, 0x2f, 0x66, 0x72,
            0x65, 0x71, 0x75, 0x65,
            0x6e, 0x63, 0x79, 0x0,
            0x2c, 0x66, 0x0,  0x0,
            0x43, 0xdc, 0x0,  0x0,
        ]
    )

    message_2 = (
        (b'/foo', [1000, -1, b'hello', approx(1.234), approx(5.678)]),
        [
            0x2f, 0x66, 0x6f, 0x6f,
            0x0,  0x0,  0x0,  0x0,
            0x2c, 0x69, 0x69, 0x73,
            0x66, 0x66, 0x0,  0x0,
            0x0,  0x0,  0x3,  0xe8,
            0xff, 0xff, 0xff, 0xff,
            0x68, 0x65, 0x6c, 0x6c,
            0x6f, 0x0,  0x0,  0x0,
            0x3f, 0x9d, 0xf3, 0xb6,
            0x40, 0xb5, 0xb2, 0x2d,
        ]
    )

    tests = (
        message_1,
        message_2,
        message_1,
        message_2,
    )

    for source, msg in tests:
        msg = struct.pack('>%iB' % len(msg), *msg)
        assert read_message(msg)[::2] == source
        data += struct.pack('>i', len(msg)) + msg

    timetag, messages = read_bundle(data)
    for test, r in zip(tests, messages):
        assert (r[0], r[2]) == test[0]


def tests_format():
    message_1 = (
        (b'/oscillator/4/frequency', [440.0]),
        [
            0x2f, 0x6f, 0x73, 0x63,
            0x69, 0x6c, 0x6c, 0x61,
            0x74, 0x6f, 0x72, 0x2f,
            0x34, 0x2f, 0x66, 0x72,
            0x65, 0x71, 0x75, 0x65,
            0x6e, 0x63, 0x79, 0x0,
            0x2c, 0x66, 0x0,  0x0,
            0x43, 0xdc, 0x0,  0x0,
        ]
    )

    message_2 = (
        (b'/foo', [1000, -1, b'hello', 1.234, 5.678]),
        [
            0x2f, 0x66, 0x6f, 0x6f,
            0x0,  0x0,  0x0,  0x0,
            0x2c, 0x69, 0x69, 0x73,
            0x66, 0x66, 0x0,  0x0,
            0x0,  0x0,  0x3,  0xe8,
            0xff, 0xff, 0xff, 0xff,
            0x68, 0x65, 0x6c, 0x6c,
            0x6f, 0x0,  0x0,  0x0,
            0x3f, 0x9d, 0xf3, 0xb6,
            0x40, 0xb5, 0xb2, 0x2d,
        ]
    )

    source, result = message_1
    result = struct.pack('>%iB' % len(result), *result)
    assert format_message(*source) == result
    assert read_message(format_message(*source))[::2] == source
