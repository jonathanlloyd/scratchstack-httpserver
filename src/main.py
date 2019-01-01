import json
import random
import logging

from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime

import scratchsocket
import models
import parser
import serializer

PORT = 8000

log = logging.getLogger('scratchserver')
logging_handler = logging.StreamHandler()
logging_formatter = logging.Formatter(\
    "%(asctime)s - %(levelname)s - %(name)s: %(message)s")
logging_handler.setFormatter(logging_formatter)
log.addHandler(logging_handler)
log.setLevel(logging.DEBUG)

def make_timestamp():
    now = datetime.now()
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)

parser = parser.Parser()
def process_byte(byte):
    req = parser.consume_byte(byte)
    if req is not None:
        log.info(f"{req.method} {req.path}")
        res = handle_request(req)
        res.headers['Server'] = 'scratchserver'
        res.headers['Date'] = make_timestamp()
        res.headers['Content-Length'] = str(len(res.body.encode('utf-8')))
        socket.write(serializer.serialize_response(res))
        socket.close_client_conn()

def handle_request(req):
    return models.Response(
        status_code=200,
        reason_phrase='OK',
        headers={'Content-Type': 'application/json'},
        body=json.dumps(req.headers),
    )

socket = scratchsocket.InboundSocket()
log.info(f"Listening on port {PORT}...")
socket.listen(PORT, process_byte)
