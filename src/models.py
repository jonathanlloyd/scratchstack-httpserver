from dataclasses import dataclass

@dataclass
class Request:
    method: str
    path: str
    headers: dict
    body: bytes

@dataclass
class Response:
    status: int
    message: str
    body: bytes
