#!/usr/bin/env python

"""Tests for `spade_pubsub` package."""
from spade.behaviour import OneShotBehaviour

from .factories import MockedPubSubAgentFactory

AGENT_JID = "pubsuba@gtirouter.dsic.upv.es"
PUBSUB_JID = "pubsub.gtirouter.dsic.upv.es"
TEST_NODE = "Test_Node"


def test_delete_node():
    agent = MockedPubSubAgentFactory(jid=AGENT_JID)

    future = agent.start(auto_register=True)
    assert future.result() is None
    assert agent.is_alive() is True

    class DeleteNodeBehaviour(OneShotBehaviour):
        async def run(self):
            await self.agent.pubsub.delete(PUBSUB_JID, TEST_NODE)
            result = await self.agent.pubsub.get_nodes(PUBSUB_JID)
            self.kill(exit_code=result)

    behaviour = DeleteNodeBehaviour()
    agent.add_behaviour(behaviour)
    behaviour.join()

    assert len(behaviour.exit_code) == 0

    future = agent.stop()
    future.result()
    assert agent.is_alive() is False


def test_create_node():
    agent = MockedPubSubAgentFactory(jid=AGENT_JID)

    future = agent.start(auto_register=True)
    assert future.result() is None
    assert agent.is_alive() is True

    class CreateNodeBehaviour(OneShotBehaviour):
        async def run(self):
            try:
                await self.agent.pubsub.create(PUBSUB_JID, TEST_NODE)
                result = await self.agent.pubsub.get_nodes(PUBSUB_JID)
                await self.agent.pubsub.delete(PUBSUB_JID, TEST_NODE)
                self.kill(exit_code=result)
            except Exception as e:
                print(f"EXCEPTION: {e}")

    behaviour = CreateNodeBehaviour()
    agent.add_behaviour(behaviour)
    behaviour.join()

    assert behaviour.exit_code[0][0] == TEST_NODE

    future = agent.stop()
    future.result()
    assert agent.is_alive() is False


def test_purge(payload):
    agent = MockedPubSubAgentFactory(jid=AGENT_JID)

    future = agent.start(auto_register=True)
    assert future.result() is None
    assert agent.is_alive() is True

    class PurgeNodeBehaviour(OneShotBehaviour):
        async def run(self):
            await self.agent.pubsub.create(PUBSUB_JID, TEST_NODE)
            await self.agent.pubsub.publish(PUBSUB_JID, TEST_NODE, payload)
            result1 = await self.agent.pubsub.get_nodes(PUBSUB_JID)
            await self.agent.pubsub.purge(PUBSUB_JID, TEST_NODE)
            result2 = await self.agent.pubsub.get_nodes(PUBSUB_JID)
            await self.agent.pubsub.delete(PUBSUB_JID, TEST_NODE)
            self.kill(exit_code=(result1, result2))

    behaviour = PurgeNodeBehaviour()
    agent.add_behaviour(behaviour)
    behaviour.join()

    assert len(behaviour.exit_code[0]) == 1
    assert behaviour.exit_code[0][0][1] is None
    assert len(behaviour.exit_code[1]) == 1
    assert behaviour.exit_code[1][0][1] is None

    future = agent.stop()
    future.result()
    assert agent.is_alive() is False


def test_subscribe():
    agent = MockedPubSubAgentFactory(jid=AGENT_JID)

    future = agent.start(auto_register=True)
    assert future.result() is None
    assert agent.is_alive() is True

    class SubscribeBehaviour(OneShotBehaviour):
        async def run(self):
            await self.agent.pubsub.subscribe(PUBSUB_JID, TEST_NODE)
            result = await self.agent.pubsub.get_node_subscriptions(
                PUBSUB_JID, TEST_NODE
            )
            self.kill(exit_code=result)

    behaviour = SubscribeBehaviour()
    agent.add_behaviour(behaviour)
    behaviour.join()

    assert len(behaviour.exit_code) == 1
    assert behaviour.exit_code[0] == AGENT_JID

    future = agent.stop()
    future.result()
    assert agent.is_alive() is False
