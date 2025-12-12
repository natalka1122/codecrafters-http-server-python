from pathlib import Path
from typing import Optional

from app.packet import HTTPRequest, HTTPResponse

ECHO_PATH = "/echo/"
FILES_PATH = "/files/"
USER_AGENT = "User-Agent"
CONTENT_TYPE = "Content-Type"
CONTENT_LENGTH = "Content-Length"
OK = "OK"
NOT_FOUND = "Not Found"
NOT_FOUND_RESPONSE = HTTPResponse(404, NOT_FOUND, headers={}, body="")


def processor(request: HTTPRequest, directory: Optional[str]) -> HTTPResponse:
    match request.request_target:
        case "/":
            return HTTPResponse(200, OK, {}, body="")
        case "/user-agent":
            user_agent: str = request.headers.get(USER_AGENT, "")
            headers = {CONTENT_TYPE: "text/plain", CONTENT_LENGTH: str(len(user_agent))}
            return HTTPResponse(200, OK, headers=headers, body=user_agent)
        case s if s.startswith(ECHO_PATH):
            echo_text = request.request_target[len(ECHO_PATH) :]
            headers = {CONTENT_TYPE: "text/plain", CONTENT_LENGTH: str(len(echo_text))}
            return HTTPResponse(200, OK, headers=headers, body=echo_text)
        case s if s.startswith(FILES_PATH):
            if directory is None:
                return NOT_FOUND_RESPONSE
            file_path = request.request_target[len(FILES_PATH) :]
            try:
                with open(Path(directory) / file_path, "r") as f:
                    content = f.read()
            except OSError:
                return NOT_FOUND_RESPONSE
            headers = {CONTENT_TYPE: "application/octet-stream", CONTENT_LENGTH: str(len(content))}
            return HTTPResponse(200, OK, headers=headers, body=content)
        case _:
            return NOT_FOUND_RESPONSE
