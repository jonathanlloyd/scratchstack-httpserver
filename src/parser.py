from dataclasses import dataclass
from enum import Enum
import string

from models import Request

TOKEN_CHARS = string.ascii_letters + string.digits + ''.join([
    '!', '#', '$', '%', '&', '\'', '*', '+', '-', '.', '^', '_', '`', '|', '~',
])

def chars_are_valid(string, valid_chars):
    return all([c in valid_chars for c in string])

# Request Line

METHOD_CHARS = TOKEN_CHARS
SEGMENT_CHARS = string.ascii_letters + string.digits + ''.join([
    '-', '_', '.',
])

@dataclass
class RequestLine:
    method: str
    path: str
    version: str

    @staticmethod
    def from_bytes(rl_bytes):
        rl_string = rl_bytes.decode('ascii')
        rl_parts = rl_string.split(' ')
        if len(rl_parts) != 3:
            raise ValueError('Request line has incorrect number of parts')

        # Method
        method = rl_parts[0]
        if method == '':
            raise ValueError('Method cannot be the empty string')
        if not chars_are_valid(method, METHOD_CHARS):
            raise ValueError('Invalid character in method')

        # Path
        path = rl_parts[1]
        if path == '':
            raise ValueError('Path cannot be the empty string')
        ## Only working with absolute paths, must begin with "/"
        if path[0] != '/':
            raise ValueError('Path must begin with "/"')
        path_segments = path.split('/')
        for segment in path_segments:
            if not chars_are_valid(segment, SEGMENT_CHARS):
                raise ValueError('Path segment contains an invalid character')

        # Version
        version = rl_parts[2]
        if version != 'HTTP/1.1':
            raise ValueError('Invalid HTTP version')

        return RequestLine(method, path, '1.1')


FIELD_NAME_CHARS = TOKEN_CHARS
FIELD_VALUE_CHARS = string.printable

def headers_from_bytes(headers_bytes):
    headers_string = headers_bytes.decode('ascii')
    header_strings = headers_string.split('\r\n')
    headers = {}
    for header_string in header_strings:
        header_parts = header_string.split(':', 1)
        if len(header_parts) != 2:
            raise ValueError('Invalid header: no ":" separator')

        field_name = header_parts[0]
        if field_name == '':
            raise ValueError('Field name cannot be the empty string')
        if not chars_are_valid(field_name, FIELD_NAME_CHARS):
            raise ValueError('Invalid character in field name')

        field_value = header_parts[1]
        field_value = field_value.strip() # Remove leading and trailing whitespace
        if field_value == '':
            raise ValueError('Field value cannot be the empty string')
        if not chars_are_valid(field_value, FIELD_VALUE_CHARS):
            raise ValueError('Invalid character in field value')

        headers[field_name.lower()] = field_value

    return headers


class Parser:
    def __init__(self):
        self._buffer = b''

    def consume_byte(self, byte):
        self._buffer += byte
        trailer = self._buffer[-4:]
        if trailer == b'\r\n\r\n':
            stripped = self._buffer[:-4]
            lines = stripped.split(b'\r\n')

            if len(lines) < 1:
                raise ValueError('Invalid request: Not enough lines')

            request_line = RequestLine.from_bytes(lines[0])
            headers = headers_from_bytes(b'\r\n'.join(lines[1:]))

            self._buffer = b''
            return Request(
                method=request_line.method,
                path=request_line.path,
                headers=headers,
                body=None,
            )

        else:
            return None
