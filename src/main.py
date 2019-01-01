import random

import scratchsocket
import parser

bytes_so_far = b''
responded = False
response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{}\r\n'

parser = parser.Parser()

def make_response(body):
    return response.format(body).encode('utf8')

def process_byte(byte):
    req = parser.consume_byte(byte)
    if req is not None:
        print('Got req:', req)
        print('Responding')
        socket.write(make_response(req.path))
        responded = True
        socket.close_client_conn()


socket = scratchsocket.InboundSocket()
socket.listen(8080, process_byte)
