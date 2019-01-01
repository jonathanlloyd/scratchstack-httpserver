from dataclasses import dataclass
from enum import Enum
import string

from models import Request

# Request Line

@dataclass
class RequestLine:
    method: str
    path: str

class RequestLineStates(Enum):
    METHOD = 1
    PATH = 2
    VERSION = 3
    TRAILER = 4

class RequestLineParser:
    METHOD_ALLOWED_CHARS = string.ascii_uppercase
    PATH_ALLOWED_CHARS = string.printable

    def __init__(self):
        self._buffer = b''
        self._method = ''
        self._path = ''
        self._version = ''
        self._state = RequestLineStates.METHOD

    def consume_byte(self, byte):
        self._buffer += byte
        char = byte.decode('utf-8')

        if self._state == RequestLineStates.METHOD:
            if char == ' ':
                self._state = RequestLineStates.PATH
            elif char in RequestLineParser.METHOD_ALLOWED_CHARS:
                self._method += char
            else:
                raise RuntimeError('Invalid byte in method')

            return None

        elif self._state == RequestLineStates.PATH:
            if char == ' ':
                self._state = RequestLineStates.VERSION
            elif char in RequestLineParser.PATH_ALLOWED_CHARS:
                self._path += char
            else:
                raise RuntimeError('Invalid byte in path')

            return None

        elif self._state == RequestLineStates.VERSION:
            if char == '\r':
                self._state = RequestLineStates.TRAILER
            elif char in RequestLineParser.PATH_ALLOWED_CHARS:
                self._version += char
            else:
                raise RuntimeError('Invalid byte in version')

            return None

        elif self._state == RequestLineStates.TRAILER:
            if char == '\n':
                if self._version.upper() != 'HTTP/1.1':
                    raise RuntimeError('Unsupported version')
                num_used_chars = len(self._buffer)
                return RequestLine(self._method, self._path), num_used_chars,
            else:
                raise RuntimeError('Invalid byte in trailer')

        else:
            raise RuntimeError(f"Invalid state: {self._state}")


class Parser:
    def __init__(self):
        self._buffer = b''

    def consume_byte(self, byte):
        self._buffer += byte
        if self._buffer[-4:] == b'\r\n\r\n':
            stripped = self._buffer[:-4].decode('utf-8')
            lines = stripped.split('\r\n')

            request_line = lines[0]
            [method, path, _] = request_line.split(' ')

            unparsed_headers = lines[1:]
            headers = {}
            for unparsed_header in unparsed_headers:
                [name, value] = unparsed_header.split(': ')
                headers[name.lower()] = value

            self._buffer = b''
            return Request(
                method=method,
                path=path,
                headers=headers,
                body=None,
            )

        else:
            return None
