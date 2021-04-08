import factory

from unittest.mock import Mock

from aioxmpp.testutils import CoroutineMock
from spade.agent import Agent

from spade_pubsub import PubSubMixin


class MockedPubSubAgent(PubSubMixin, Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self._async_connect = CoroutineMock()
        # self._async_register = CoroutineMock()
        # self.conn_coro = Mock()
        # self.conn_coro.__aexit__ = CoroutineMock()
        # self.stream = Mock()


class MockedPubSubAgentFactory(factory.Factory):
    class Meta:
        model = MockedPubSubAgent

    jid = "fake@jid"
    password = "fake_password"
