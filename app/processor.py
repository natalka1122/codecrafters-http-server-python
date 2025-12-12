from pathlib import Path
from typing import Optional

from app.const import (
    CONTENT_LENGTH,
    CONTENT_TYPE,
    ECHO_PATH,
    FILES_PATH,
    GET,
    NOT_FOUND,
    OK,
    POST,
    USER_AGENT,
)
from app.packet import HTTPRequest, HTTPResponse

NOT_FOUND_RESPONSE = HTTPResponse(404, NOT_FOUND)


def processor(request: HTTPRequest, directory: Optional[str]) -> tuple[bool, HTTPResponse]:
    should_close = request.headers.get("Connection", "") == "close"
    if request.method == GET:
        match request.request_target:
            case "/":
                return should_close, HTTPResponse(200)
            case "/user-agent":
                user_agent: str = request.headers.get(USER_AGENT, "")
                headers = {CONTENT_TYPE: "text/plain", CONTENT_LENGTH: str(len(user_agent))}
                return should_close, HTTPResponse(200, OK, headers=headers, body=user_agent)
            case s if s.startswith(ECHO_PATH):
                echo_text = request.request_target[len(ECHO_PATH) :]
                headers = {CONTENT_TYPE: "text/plain", CONTENT_LENGTH: str(len(echo_text))}
                return should_close, HTTPResponse(200, OK, headers=headers, body=echo_text)
            case s if s.startswith(FILES_PATH):
                if directory is None:
                    return should_close, NOT_FOUND_RESPONSE
                file_path = request.request_target[len(FILES_PATH) :]
                try:
                    with open(Path(directory) / file_path, "r") as f:
                        content = f.read()
                except OSError:
                    return should_close, NOT_FOUND_RESPONSE
                headers = {
                    CONTENT_TYPE: "application/octet-stream",
                    CONTENT_LENGTH: str(len(content)),
                }
                return should_close, HTTPResponse(200, OK, headers=headers, body=content)
            case _:
                return should_close, NOT_FOUND_RESPONSE
    elif request.method == POST:
        match request.request_target:
            case s if s.startswith(FILES_PATH):
                if directory is None:
                    return should_close, NOT_FOUND_RESPONSE
                file_path = file_path = request.request_target[len(FILES_PATH) :]
                try:
                    with open(Path(directory) / file_path, "w") as f:
                        f.write(request.body)
                except OSError:
                    return should_close, NOT_FOUND_RESPONSE
                return should_close, HTTPResponse(201, "Created")
            case _:
                return should_close, NOT_FOUND_RESPONSE
    else:
        return should_close, NOT_FOUND_RESPONSE
