from dataclasses import dataclass

@dataclass
class Request:
    method: str
    path: str
    headers: dict
    body: bytes

@dataclass
class Response:
    status_code: int
    reason_phrase: str
    headers: dict
    body: bytes
