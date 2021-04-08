import aioxmpp
import aioxmpp.pubsub.xso as pubsub_xso
import pytest
from spade.container import Container
from spade import quit_spade


@pytest.fixture(autouse=True)
def run_around_tests():
    # Code that will run before your test, for example:
    # A test function will be run at this point
    container = Container()
    if not container.is_running:
        container.__init__()
    yield
    # Code that will run after your test, for example:
    quit_spade()


@pytest.fixture(scope="module", autouse=True)
def cleanup(request):
    quit_spade()


@pubsub_xso.as_payload_class
class SomePayload(aioxmpp.xso.XSO):
    TAG = "spade.pubsub.test_service", "foo"


@pytest.fixture()
def payload():
    return SomePayload()
