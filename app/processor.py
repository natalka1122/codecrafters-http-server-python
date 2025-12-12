END_LINE = b"\r\n"


def processor(request: bytes) -> bytes:
    lines = request.split(END_LINE)
    try:
        request_target = lines[0].split(b" ")[1]
    except IndexError:
        return b"TODO"
    if request_target == b"/":
        return b"HTTP/1.1 200 OK\r\n\r\n"
    else:
        return b"HTTP/1.1 404 Not Found\r\n\r\n"
