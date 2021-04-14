import factory
from spade.agent import Agent

from spade_pubsub import PubSubMixin


class PubSubAgent(PubSubMixin, Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = None

    def callback(self, jid, node, item, message=None):
        self.result = item.registered_payload.data


class PubSubAgentFactory(factory.Factory):
    class Meta:
        model = PubSubAgent

    jid = "fake@jid"
    password = "fake_password"
