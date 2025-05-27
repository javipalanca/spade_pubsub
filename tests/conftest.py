import asyncio
import pytest
import pytest_asyncio

from loguru import logger
from pyjabber.server import Server, Parameters


@pytest.fixture(scope="module", autouse=True)
def cleanup(request):
    pass


@pytest_asyncio.fixture
async def server():
    logger.remove()

    server = Server(Parameters(database_in_memory=True))

    task = asyncio.create_task(server.start())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
