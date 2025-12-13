from typing import Callable, Optional

from app import const, handlers
from app.packet import HTTPRequest, HTTPResponse


def processor(request: HTTPRequest, directory: Optional[str]) -> tuple[bool, HTTPResponse]:
    should_close = request.headers.get(b"Connection", b"") == b"close"
    should_gzip = const.GZIP in request.headers.get(b"Accept-Encoding", b"").split(b", ")
    handler = get_handler(request)
    response = handler(request, directory)
    if should_close:
        response.headers[b"Connection"] = b"close"
    if should_gzip:
        response.gzip()
    return should_close, response


def get_handler(request: HTTPRequest) -> Callable[[HTTPRequest, Optional[str]], HTTPResponse]:
    if request.method == const.GET:
        return _get_get_handler(request)
    elif request.method == const.POST and request.request_target.startswith(const.FILES_PATH):
        handler = handlers.do_write_to_file
    else:
        handler = handlers.do_not_found
    return handler


def _get_get_handler(request: HTTPRequest) -> Callable[[HTTPRequest, Optional[str]], HTTPResponse]:
    match request.request_target:
        case b"/":
            handler = handlers.do_root
        case b"/user-agent":
            handler = handlers.do_user_agent
        case s if s.startswith(const.ECHO_PATH):
            handler = handlers.do_echo_reply
        case s if s.startswith(const.FILES_PATH):
            handler = handlers.do_read_from_file
        case _:
            handler = handlers.do_not_found
    return handler
