from pathlib import Path
from typing import Optional

from app import const
from app.packet import HTTPRequest, HTTPResponse

NOT_FOUND_RESPONSE = HTTPResponse(404, const.NOT_FOUND, headers=dict())


def do_root(request: HTTPRequest, directory: Optional[str]) -> HTTPResponse:
    return HTTPResponse(200, const.OK, headers=dict())


def do_not_found(request: HTTPRequest, directory: Optional[str]) -> HTTPResponse:
    return NOT_FOUND_RESPONSE


def do_echo_reply(request: HTTPRequest, directory: Optional[str]) -> HTTPResponse:
    echo_text = request.request_target[len(const.ECHO_PATH) :]
    headers = {
        const.CONTENT_TYPE: b"text/plain",
        const.CONTENT_LENGTH: str(len(echo_text)).encode(),
    }
    return HTTPResponse(200, const.OK, headers=headers, body=echo_text)


def do_user_agent(request: HTTPRequest, directory: Optional[str]) -> HTTPResponse:
    user_agent: bytes = request.headers.get(const.USER_AGENT, b"")
    headers = {
        const.CONTENT_TYPE: b"text/plain",
        const.CONTENT_LENGTH: str(len(user_agent)).encode(),
    }
    return HTTPResponse(200, const.OK, headers=headers, body=user_agent)


def do_read_from_file(request: HTTPRequest, directory: Optional[str]) -> HTTPResponse:
    if directory is None:
        return NOT_FOUND_RESPONSE
    file_path = request.request_target[len(const.FILES_PATH) :].decode()
    try:
        with open(Path(directory) / file_path, "rb") as f:
            content = f.read()
    except OSError:
        return NOT_FOUND_RESPONSE
    headers = {
        const.CONTENT_TYPE: b"application/octet-stream",
        const.CONTENT_LENGTH: str(len(content)).encode(),
    }
    return HTTPResponse(200, const.OK, headers=headers, body=content)


def do_write_to_file(request: HTTPRequest, directory: Optional[str]) -> HTTPResponse:
    if directory is None:
        return NOT_FOUND_RESPONSE
    file_path = request.request_target[len(const.FILES_PATH) :].decode()
    try:
        with open(Path(directory) / file_path, "wb") as f:
            f.write(request.body)
    except OSError:
        return NOT_FOUND_RESPONSE
    return HTTPResponse(201, b"Created", headers=dict())
