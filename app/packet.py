from dataclasses import dataclass

END_LINE = "\r\n"


@dataclass
class HTTPRequest:
    request_target: str
    headers: dict[str, str]

    @classmethod
    def from_bytes(cls, data: bytes) -> "HTTPRequest":  # noqa: WPS210
        lines = data.decode().split(END_LINE)
        _, request_target, _ = lines[0].split(" ")
        headers: dict[str, str] = {}
        for line in lines[1:]:
            if len(line) == 0:
                break
            key, value = line.split(": ")
            headers[key] = value
        return HTTPRequest(request_target=request_target, headers=headers)


@dataclass
class HTTPResponse:
    status_code: int
    reason_phrase: str
    headers: dict[str, str]
    body: str

    @property
    def to_bytes(self) -> bytes:
        result: list[str] = [f"HTTP/1.1 {self.status_code} {self.reason_phrase}{END_LINE}"]
        for key, value in self.headers.items():
            result.append(f"{key}: {value}{END_LINE}")
        result.append(f"{END_LINE}{self.body}")
        return "".join(result).encode()
