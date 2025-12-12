import asyncio
import traceback
from typing import Optional

from app.connection import Connection
from app.const import DEFAULT_PORT, HOST
from app.exceptions import ReaderClosedError, WriterClosedError
from app.logging_config import get_logger
from app.packet import HTTPRequest
from app.processor import processor
from app.server_state import ServerState

logger = get_logger(__name__)


async def http_server(  # noqa: WPS213
    directory: Optional[str],
    shutdown_event: asyncio.Event,
    started_event: asyncio.Event,
) -> None:
    server_state = ServerState(directory=directory)
    try:
        server = await asyncio.start_server(
            lambda reader, writer: handle_client(
                reader=reader, writer=writer, server_state=server_state
            ),
            HOST,
            DEFAULT_PORT,
        )
    except OSError as error:
        logger.error(f"Cannot start server: {error}")
        shutdown_event.set()
        started_event.set()
        return
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    logger.info(f"Server is serving on {addrs}")

    started_event.set()
    logger.info("Everybody started")
    await shutdown_event.wait()
    logger.info("Shutdown signal received, stopping workers...")

    async with server:
        # Wait for shutdown or cancellation
        try:
            await shutdown_event.wait()  # instead of serve_forever()
        except asyncio.CancelledError:
            logger.info("Server cancelled, shutting down...")
            raise
        finally:
            logger.info("Closing server...")
            await close_connections(list(server_state.connections.values()))
    logger.info("All workers stopped. Goodbye!")


async def handle_client(  # noqa: WPS213
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, server_state: ServerState
) -> None:
    connection = server_state.add_new_connection(reader=reader, writer=writer)
    logger.debug(f"{connection.peername}: New connection")

    try:  # noqa: WPS229
        data_parsed = HTTPRequest.from_bytes(await connection.read())
        logger.debug(f"data_parsed = {data_parsed!r}")
        response = processor(data_parsed, directory=server_state.directory)
        logger.debug(f"response = {response}")
        await connection.write(response.to_bytes)
    except (ReaderClosedError, WriterClosedError):
        logger.debug(f"{connection.peername}: Client disconnected")
    except asyncio.CancelledError:
        logger.info(f"{connection.peername}: Connection handler cancelled.")
        raise  # Don't clean up - server will handle it
    except Exception as e:
        logger.error(f"{connection.peername}: Error in client handler: {type(e)} {e}")
        logger.error(traceback.format_exc())

    connection.closing.set()
    # Clean up the connection (only reached if not cancelled)
    logger.info(f"{connection.peername}: Closing connection")
    await server_state.purge_connection(connection)
    logger.debug(f"{connection.peername}: Connection closed")


async def close_connections(connections: list[Connection]) -> None:
    if not connections:
        logger.info("Server closed")
        return
    tasks: list[asyncio.Task[bool]] = []
    for connection in connections:
        connection.closing.set()
        tasks.append(asyncio.create_task(connection.closed.wait()))
    done, pending = await asyncio.wait(tasks)
    len_pending = len(pending)
    if len_pending > 0:
        logger.info(f"Closed {len(done)} connections, {len_pending} connections left")
    else:
        logger.info(f"Closed all {len(done)} connections")
