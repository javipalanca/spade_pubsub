import factory
import slixmpp.stanza
from spade.agent import Agent

from spade_pubsub import PubSubMixin


class PubSubAgent(PubSubMixin, Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = None

    def callback(self, message: slixmpp.stanza.Message):
        self.result = message.get_payload()


class PubSubAgentFactory(factory.Factory):
    class Meta:
        model = PubSubAgent

    jid = "fake@jid"
    password = "fake_password"
