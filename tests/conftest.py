import asyncio
import pytest
import pytest_asyncio

from loguru import logger
from pyjabber.server import Server, Parameters


@pytest.fixture(scope="module", autouse=True)
def cleanup(request):
    pass


@pytest_asyncio.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def server(event_loop):
    logger.remove()

    server = Server(Parameters(database_in_memory=True))

    task = event_loop.create_task(server.start())
    yield task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
