END_LINE = b"\r\n"
ECHO_PATH = b"/echo/"
USER_AGENT = b"User-Agent".lower()


def processor(request: bytes) -> bytes:
    lines = request.split(END_LINE)
    try:
        request_target = lines[0].split(b" ")[1]
    except IndexError:
        return b"TODO"
    headers = {}
    for line in lines[1:-1]:
        try:
            key, value = line.split(b": ")
        except ValueError:
            continue
        headers[key.lower()] = value
    if request_target == b"/":
        return b"HTTP/1.1 200 OK\r\n\r\n"
    elif request_target.startswith(ECHO_PATH):
        echo_text = request_target[len(ECHO_PATH) :]
        result = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo_text)}\r\n\r\n"
        return result.encode() + echo_text
    elif request_target == b"/user-agent":
        user_agent: str = headers.get(USER_AGENT, b"").decode("utf-8")
        result = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}"
        return result.encode()
    else:
        return b"HTTP/1.1 404 Not Found\r\n\r\n"
