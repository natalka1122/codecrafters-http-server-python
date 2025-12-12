END_LINE = b"\r\n"
ECHO_PATH = b"/echo/"


def processor(request: bytes) -> bytes:
    lines = request.split(END_LINE)
    try:
        request_target = lines[0].split(b" ")[1]
    except IndexError:
        return b"TODO"
    if request_target == b"/":
        return b"HTTP/1.1 200 OK\r\n\r\n"
    elif request_target.startswith(ECHO_PATH):
        echo_text = request_target[len(ECHO_PATH) :]
        result = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_text)}\r\n\r\n"
        return result.encode() + echo_text
    else:
        return b"HTTP/1.1 404 Not Found\r\n\r\n"
