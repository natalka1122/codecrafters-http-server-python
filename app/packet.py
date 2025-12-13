import gzip
from dataclasses import dataclass

from app.const import CONTENT_LENGTH, END_LINE, GZIP


@dataclass
class HTTPRequest:
    method: bytes
    request_target: bytes
    headers: dict[bytes, bytes]
    body: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> "HTTPRequest":  # noqa: WPS210
        lines = data.split(END_LINE)
        method, request_target, _ = lines[0].split(b" ")
        headers: dict[bytes, bytes] = {}
        index = 1
        while index < len(lines):
            line = lines[index]
            if len(line) == 0:
                break
            key, value = line.split(b": ")
            headers[key] = value
            index += 1
        body = END_LINE.join(lines[index + 1 :])
        return HTTPRequest(method=method, request_target=request_target, headers=headers, body=body)


@dataclass
class HTTPResponse:
    status_code: int
    reason_phrase: bytes
    headers: dict[bytes, bytes]
    body: bytes = b""
    _should_gzip: bool = False

    def gzip(self) -> None:
        if self._should_gzip:
            raise NotImplementedError
        self._should_gzip = True
        self.headers[b"Content-Encoding"] = GZIP
        self.body = gzip.compress(self.body)
        self.headers[CONTENT_LENGTH] = str(len(self.body)).encode()

    @property
    def to_bytes(self) -> bytes:
        result: list[bytes] = [
            f"HTTP/1.1 {self.status_code} ".encode(),
            self.reason_phrase,
            END_LINE,
        ]
        for key, value in self.headers.items():
            result.extend([key, b": ", value, END_LINE])
        result.append(END_LINE)
        result.append(self.body)
        return b"".join(result)
