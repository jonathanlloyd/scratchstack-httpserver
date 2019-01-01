import unittest

from models import Request
import parser

class TestRequestLineParser(unittest.TestCase):
    def test_basic_request_line(self):
        request_line_bytes = b'GET /index.html HTTP/1.1'
        request_line = parser.RequestLine.from_bytes(request_line_bytes)

        assert request_line.method == 'GET'
        assert request_line.path == '/index.html'
        assert request_line.version == '1.1'

    def test_invalid_method_char(self):
        request_line_bytes = b'GE:T /index.html HTTP/1.1'

        try:
            request_line = parser.RequestLine.from_bytes(request_line_bytes)
            self.fail()
        except ValueError as e:
            assert str(e) == 'Invalid character in method'

    def test_missing_method(self):
        request_line_bytes = b' /index.html HTTP/1.1'

        try:
            request_line = parser.RequestLine.from_bytes(request_line_bytes)
            self.fail()
        except ValueError as e:
            assert str(e) == 'Method cannot be the empty string'

    def test_missing_space_after_method(self):
        request_line_bytes = b'GET/index.html HTTP/1.1'

        try:
            request_line = parser.RequestLine.from_bytes(request_line_bytes)
            self.fail()
        except ValueError as e:
            assert str(e) == 'Request line has incorrect number of parts'

    def test_root_path(self):
        request_line_bytes = b'GET / HTTP/1.1'
        request_line = parser.RequestLine.from_bytes(request_line_bytes)

        assert request_line.method == 'GET'
        assert request_line.path == '/'
        assert request_line.version == '1.1'

    def test_multi_part_path(self):
        request_line_bytes = b'GET /a/b/c HTTP/1.1'
        request_line = parser.RequestLine.from_bytes(request_line_bytes)

        assert request_line.method == 'GET'
        assert request_line.path == '/a/b/c'
        assert request_line.version == '1.1'

    def test_trailing_slash(self):
        request_line_bytes = b'GET /a/ HTTP/1.1'
        request_line = parser.RequestLine.from_bytes(request_line_bytes)

        assert request_line.method == 'GET'
        assert request_line.path == '/a/'
        assert request_line.version == '1.1'

    def test_missing_slash(self):
        request_line_bytes = b'GET index.html HTTP/1.1'

        try:
            request_line = parser.RequestLine.from_bytes(request_line_bytes)
            self.fail()
        except ValueError as e:
            assert str(e) == 'Path must begin with "/"'

    def test_missing_path(self):
        request_line_bytes = b'GET  HTTP/1.1'

        try:
            request_line = parser.RequestLine.from_bytes(request_line_bytes)
            self.fail()
        except ValueError as e:
            assert str(e) == 'Path cannot be the empty string'

    def test_invalid_path_char(self):
        request_line_bytes = b'GET /:/b/c HTTP/1.1'

        try:
            request_line = parser.RequestLine.from_bytes(request_line_bytes)
            self.fail()
        except ValueError as e:
            assert str(e) == 'Path segment contains an invalid character'

    def test_invalid_http_version(self):
        request_line_bytes = b'GET /index.html HTTP/2.1'

        try:
            request_line = parser.RequestLine.from_bytes(request_line_bytes)
            self.fail()
        except ValueError as e:
            assert str(e) == 'Invalid HTTP version'

class TestHeadersParser(unittest.TestCase):
    def test_basic_headers(self):
        headers_bytes = b'Host: example.com\r\nContent-Length: 32'
        headers = parser.headers_from_bytes(headers_bytes)

        assert headers == {
            'host': 'example.com',
            'content-length': '32',
        }

    def test_single_header(self):
        headers_bytes = b'Host: example.com'
        headers = parser.headers_from_bytes(headers_bytes)

        assert headers == {
            'host': 'example.com',
        }

    def test_leading_whitespace(self):
        headers_bytes = b'Host:   example.com'
        headers = parser.headers_from_bytes(headers_bytes)

        assert headers == {
            'host': 'example.com',
        }

    def test_trailing_whitespace(self):
        headers_bytes = b'Host: example.com    '
        headers = parser.headers_from_bytes(headers_bytes)

        assert headers == {
            'host': 'example.com',
        }

    def test_no_separator(self):
        headers_bytes = b'Host example.com'

        try:
            parser.headers_from_bytes(headers_bytes)
            self.fail()
        except ValueError as e:
            assert str(e) == 'Invalid header: no ":" separator'

    def test_missing_field_name(self):
        headers_bytes = b': example.com'

        try:
            parser.headers_from_bytes(headers_bytes)
            self.fail()
        except ValueError as e:
            assert str(e) == 'Field name cannot be the empty string'

    def test_invalid_field_name(self):
        headers_bytes = b'\x00: example.com'

        try:
            parser.headers_from_bytes(headers_bytes)
            self.fail()
        except ValueError as e:
            assert str(e) == 'Invalid character in field name'

    def test_missing_field_value(self):
        headers_bytes = b'Host:   '

        try:
            parser.headers_from_bytes(headers_bytes)
            self.fail()
        except ValueError as e:
            assert str(e) == 'Field value cannot be the empty string'

    def test_invalid_field_value(self):
        headers_bytes = b'Host: \x00.com'

        try:
            parser.headers_from_bytes(headers_bytes)
            self.fail()
        except ValueError as e:
            assert str(e) == 'Invalid character in field value'

class TestParser(unittest.TestCase):
    def test_parse_simple_request(self):
        request_bytes = bytes_to_list(
                b'GET /index.html HTTP/1.1\r\nHost: example.com\r\n\r\n'
        )
        p = parser.Parser()

        # Add everything but the last byte
        for byte in request_bytes[:-1]:
            parsed_request = p.consume_byte(byte)
            # No request objects should be returned
            assert parsed_request is None

        # Add the last byte
        last_byte = request_bytes[-1]
        parsed_request = p.consume_byte(last_byte)

        assert isinstance(parsed_request, Request)
        assert parsed_request.method == 'GET'
        assert parsed_request.path == '/index.html'
        assert parsed_request.headers == {'host': 'example.com'}
        assert parsed_request.body == None

def bytes_to_list(b):
    return [bytes([byte]) for byte in b]

def int_to_byte(i):
    return bytes([i])
