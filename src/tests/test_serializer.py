import unittest

from models import Response
import serializer

class TestSerializeResponse(unittest.TestCase):
    def test_basic_response(self):
        response = Response(
            status_code=200,
            reason_phrase='Ok',
            headers={'Content-Length': 5},
            body='Hello',
        )

        response_bytes = serializer.serialize_response(response)

        assert response_bytes == b'HTTP/1.1 200 Ok\r\nContent-Length: 5\r\n\r\nHello'

    def test_negative_status_code(self):
        try:
            response = Response(
                status_code=-200,
                reason_phrase='Ok',
                headers={'Content-Length': 5},
                body='Hello',
            )
            serializer.serialize_response(response)
            self.fail()
        except ValueError as e:
            assert str(e) == 'Status code cannot be negative'

    def test_oversized_status_code(self):
        try:
            response = Response(
                status_code=2000,
                reason_phrase='Ok',
                headers={'Content-Length': 5},
                body='Hello',
            )
            serializer.serialize_response(response)
            self.fail()
        except ValueError as e:
            assert str(e) == 'Status code must be < 1000'
