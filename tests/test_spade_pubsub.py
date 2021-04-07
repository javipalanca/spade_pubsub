#!/usr/bin/env python

"""Tests for `spade_pubsub` package."""
from aioxmpp import JID
from spade.behaviour import OneShotBehaviour

from .factories import MockedPubSubAgentFactory

TEST_NODE = "Test_Node"

PUBSUB_JID = JID.fromstr('pubsub.gtirouter.dsic.upv.es')


def test_delete_node():
    agent = MockedPubSubAgentFactory(jid="pubsuba@gtirouter.dsic.upv.es")

    future = agent.start(auto_register=True)
    assert future.result() is None
    assert agent.is_alive() is True

    class DeleteNodeBehaviour(OneShotBehaviour):
        async def run(self):
            await self.agent.pubsub.delete(PUBSUB_JID, TEST_NODE)
            self.kill()

    behaviour = DeleteNodeBehaviour()
    agent.add_behaviour(behaviour)
    behaviour.join()

    future = agent.stop()
    future.result()
    assert agent.is_alive() is False


def test_create_node():
    agent = MockedPubSubAgentFactory(jid="pubsuba@gtirouter.dsic.upv.es")

    future = agent.start(auto_register=True)
    assert future.result() is None
    assert agent.is_alive() is True

    class CreateNodeBehaviour(OneShotBehaviour):
        async def run(self):
            await self.agent.pubsub.create(PUBSUB_JID, TEST_NODE)
            result = await self.agent.pubsub.get_nodes(PUBSUB_JID)
            self.kill(exit_code=result)

    behaviour = CreateNodeBehaviour()
    agent.add_behaviour(behaviour)
    behaviour.join()

    assert behaviour.exit_code == "AAA"

    future = agent.stop()
    future.result()
    assert agent.is_alive() is False
