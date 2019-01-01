import unittest

from models import Request
import parser

class TestRequestLineParser(unittest.TestCase):
    def test_basic_request_line(self):
        request_line_bytes = bytes_to_list(b'GET /index.html HTTP/1.1\r\n')
        p = parser.RequestLineParser()

        # Add everything but the last byte
        for byte in request_line_bytes[:-1]:
            parsed = p.consume_byte(byte)
            # Nothing should be returned
            assert parsed is None

        # Add the last byte
        last_byte = request_line_bytes[-1]
        [request_line, num_bytes] = p.consume_byte(last_byte)

        assert num_bytes == 26
        assert request_line.method == 'GET'
        assert request_line.path == '/index.html'

    def test_invalid_method(self):
        request_line_bytes = bytes_to_list(b'GET\r\n')
        p = parser.RequestLineParser()

        try:
            for byte in request_line_bytes:
                parsed = p.consume_byte(byte)
            self.assertFail()
        except RuntimeError as e:
            assert str(e) == 'Invalid byte in method'

"""
class TestParser(unittest.TestCase):
    def test_parse_simple_request(self):
        request_bytes = b'GET /index.html HTTP/1.1\r\nHost: example.com\r\n\r\n'
        parser = Parser()

        # Add everything but the last byte
        for bytent in request_bytes[:-1]:
            parsed_request = parser.consume_byte(byte)
            # No request objects should be returned
            assert parsed_request is None

        # Add the last byte
        last_byte_int = request_bytes[-1]
        last_byte = bytes([last_byte_int])
        parsed_request = parser.consume_byte(last_byte)

        assert isinstance(parsed_request, Request)
        assert parsed_request.method == 'GET'
        assert parsed_request.path == '/index.html'
        assert parsed_request.headers == {'host': 'example.com'}
        assert parsed_request.body == None
"""

def bytes_to_list(b):
    return [bytes([byte]) for byte in b]

def int_to_byte(i):
    return bytes([i])
