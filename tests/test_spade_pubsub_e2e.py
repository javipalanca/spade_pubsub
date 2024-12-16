#!/usr/bin/env python

"""Tests for `spade_pubsub` package."""
import pytest
from uuid import uuid4
from xml.etree.ElementTree import Element, fromstring
from spade.behaviour import OneShotBehaviour

from .factories import PubSubAgentFactory


XMPP_SERVER = "araylop-vrain"  # Make sure there is an XMPP server available at this address


AGENT_JID = f"pubsuba@{XMPP_SERVER}"
AGENT_JID_2 = f"pubsubb@{XMPP_SERVER}"
PUBSUB_JID = f"pubsub.{XMPP_SERVER}"
TEST_NODE = "Test_Node"
ITEM_ID = str(uuid4())
TEST_PAYLOAD = Element("test")
TEST_PAYLOAD.text = "TESTING"


@pytest.mark.asyncio
async def test_delete_node():
    agent = PubSubAgentFactory(jid=AGENT_JID)

    await agent.start(auto_register=True)
    assert agent.is_alive() is True

    agent.client.register_plugin('xep_0004')
    config_form = agent.client.plugin["xep_0004"].make_form(ftype="submit")
    config_form.addField('pubsub#persist_items', value=True)

    class DeleteNodeBehaviour(OneShotBehaviour):
        async def run(self):
            try:
                await self.agent.pubsub.create(PUBSUB_JID, TEST_NODE, config_form)
            except Exception as e:
                print(f"{e}: Node already existed.")
            await self.agent.pubsub.delete(PUBSUB_JID, TEST_NODE)
            result = await self.agent.pubsub.get_nodes(PUBSUB_JID)
            self.kill(exit_code=result)

    behaviour = DeleteNodeBehaviour()
    agent.add_behaviour(behaviour)
    await behaviour.join()

    assert len(behaviour.exit_code) == 0

    await agent.stop()
    assert agent.is_alive() is False


@pytest.mark.asyncio
async def test_create_node():
    agent = PubSubAgentFactory(jid=AGENT_JID)

    await agent.start(auto_register=True)
    assert agent.is_alive() is True

    class CreateNodeBehaviour(OneShotBehaviour):
        async def run(self):
            await self.agent.pubsub.create(PUBSUB_JID, TEST_NODE)
            result = await self.agent.pubsub.get_nodes(PUBSUB_JID)
            await self.agent.pubsub.delete(PUBSUB_JID, TEST_NODE)
            self.kill(exit_code=result)

    behaviour = CreateNodeBehaviour()
    agent.add_behaviour(behaviour)
    await behaviour.join()

    assert any([f'node="{TEST_NODE}"' in i for i in behaviour.exit_code])

    await agent.stop()
    assert agent.is_alive() is False


@pytest.mark.asyncio
async def test_purge_node():
    agent = PubSubAgentFactory(jid=AGENT_JID)

    await agent.start(auto_register=True)
    assert agent.is_alive() is True

    agent.client.register_plugin('xep_0004')
    config_form = agent.client.plugin["xep_0004"].make_form(ftype="submit")
    config_form.addField('pubsub#persist_items', value=True)

    class PurgeNodeBehaviour(OneShotBehaviour):
        async def run(self):
            await self.agent.pubsub.create(PUBSUB_JID, TEST_NODE, config_form)
            await self.agent.pubsub.publish(PUBSUB_JID, TEST_NODE, TEST_PAYLOAD)
            result1 = await self.agent.pubsub.get_items(PUBSUB_JID, TEST_NODE)
            await self.agent.pubsub.purge(PUBSUB_JID, TEST_NODE)
            result2 = await self.agent.pubsub.get_items(PUBSUB_JID, TEST_NODE)
            await self.agent.pubsub.delete(PUBSUB_JID, TEST_NODE)
            self.kill(exit_code=(result1, result2))

    behaviour = PurgeNodeBehaviour()
    agent.add_behaviour(behaviour)
    await behaviour.join()

    assert len(behaviour.exit_code[0]) == 1
    assert TEST_PAYLOAD.tag in fromstring(behaviour.exit_code[0][0]).tag
    assert TEST_PAYLOAD.text == fromstring(behaviour.exit_code[0][0]).text
    assert len(behaviour.exit_code[1]) == 0

    future = agent.stop()
    future.result()
    assert agent.is_alive() is False


@pytest.mark.asyncio
async def test_subscribe_to_node():
    agent = PubSubAgentFactory(jid=AGENT_JID)

    await agent.start(auto_register=True)
    assert agent.is_alive() is True

    class SubscribeBehaviour(OneShotBehaviour):
        async def run(self):
            await self.agent.pubsub.create(PUBSUB_JID, TEST_NODE)
            await self.agent.pubsub.subscribe(PUBSUB_JID, TEST_NODE)
            result = await self.agent.pubsub.get_node_subscriptions(
                PUBSUB_JID, TEST_NODE
            )
            await self.agent.pubsub.delete(PUBSUB_JID, TEST_NODE)
            self.kill(exit_code=result)

    behaviour = SubscribeBehaviour()
    agent.add_behaviour(behaviour)
    await behaviour.join()

    assert len(behaviour.exit_code) == 1
    assert behaviour.exit_code[0] == AGENT_JID

    await agent.stop()
    assert agent.is_alive() is False


@pytest.mark.asyncio
async def test_unsubscribe_from_node():
    agent = PubSubAgentFactory(jid=AGENT_JID)

    await agent.start(auto_register=True)
    assert agent.is_alive() is True

    class SubscribeBehaviour(OneShotBehaviour):
        async def run(self):
            await self.agent.pubsub.create(PUBSUB_JID, TEST_NODE)
            _, subid = await self.agent.pubsub.subscribe(PUBSUB_JID, TEST_NODE)
            await self.agent.pubsub.unsubscribe(PUBSUB_JID, TEST_NODE, AGENT_JID, subid)
            result = await self.agent.pubsub.get_node_subscriptions(
                PUBSUB_JID, TEST_NODE
            )
            await self.agent.pubsub.delete(PUBSUB_JID, TEST_NODE)
            self.kill(exit_code=result)

    behaviour = SubscribeBehaviour()
    agent.add_behaviour(behaviour)
    await behaviour.join()

    assert len(behaviour.exit_code) == 0

    await agent.stop()
    assert agent.is_alive() is False


@pytest.mark.asyncio
async def test_notify():
    agent = PubSubAgentFactory(jid=AGENT_JID)

    await agent.start(auto_register=True)
    assert agent.is_alive() is True

    agent.result = None

    agent.pubsub.set_on_item_published(agent.callback)

    class NotifyBehaviour(OneShotBehaviour):
        async def run(self):
            await self.agent.pubsub.create(PUBSUB_JID, TEST_NODE)
            await self.agent.pubsub.subscribe(PUBSUB_JID, TEST_NODE)
            await self.agent.pubsub.notify(PUBSUB_JID, TEST_NODE)
            await self.agent.pubsub.delete(PUBSUB_JID, TEST_NODE)

    behaviour = NotifyBehaviour()
    agent.add_behaviour(behaviour)
    await behaviour.join()

    await agent.stop()
    assert agent.is_alive() is False


async def test_publish_item():
    agent = PubSubAgentFactory(jid=AGENT_JID)

    await agent.start(auto_register=True)
    assert agent.is_alive() is True

    agent.pubsub.set_on_item_published(agent.callback)

    class PublishBehaviour(OneShotBehaviour):
        async def run(self):
            await self.agent.pubsub.create(PUBSUB_JID, TEST_NODE)
            await self.agent.pubsub.subscribe(PUBSUB_JID, TEST_NODE)
            await self.agent.pubsub.publish(PUBSUB_JID, TEST_NODE, TEST_PAYLOAD)
            items = await self.agent.pubsub.get_items(PUBSUB_JID, TEST_NODE)
            await self.agent.pubsub.delete(PUBSUB_JID, TEST_NODE)
            self.kill(exit_code=items)

    behaviour = PublishBehaviour()
    agent.add_behaviour(behaviour)
    await behaviour.join()

    assert TEST_PAYLOAD.tag in agent.result[0][0][0][0].tag
    assert agent.result[0][0][0][0].text == TEST_PAYLOAD.text
    assert TEST_PAYLOAD.text in behaviour.exit_code[0]

    await agent.stop()
    assert agent.is_alive() is False


async def test_retract_item():
    agent = PubSubAgentFactory(jid=AGENT_JID)

    await agent.start(auto_register=True)
    assert agent.is_alive() is True

    agent.client.register_plugin('xep_0004')
    config_form = agent.client.plugin["xep_0004"].make_form(ftype="submit")
    config_form.addField('pubsub#persist_items', value=True)

    class PublishBehaviour(OneShotBehaviour):
        async def run(self):
            await self.agent.pubsub.create(PUBSUB_JID, TEST_NODE, config_form)
            # for node in await self.agent.pubsub.get_nodes(PUBSUB_JID):
            #     await self.agent.pubsub.delete(PUBSUB_JID, node[0])
            await self.agent.pubsub.subscribe(PUBSUB_JID, TEST_NODE)
            await self.agent.pubsub.publish(PUBSUB_JID, TEST_NODE, TEST_PAYLOAD, ITEM_ID)
            items = await self.agent.pubsub.get_items(PUBSUB_JID, TEST_NODE)
            self.kill(exit_code=items)

    publish_behaviour = PublishBehaviour()
    agent.add_behaviour(publish_behaviour)
    await publish_behaviour.join()

    assert len(publish_behaviour.exit_code) == 1
    assert TEST_PAYLOAD.tag in fromstring(publish_behaviour.exit_code[0]).tag
    assert TEST_PAYLOAD.text == fromstring(publish_behaviour.exit_code[0]).text

    class RetractBehaviour(OneShotBehaviour):
        async def run(self):
            await self.agent.pubsub.retract(PUBSUB_JID, TEST_NODE, ITEM_ID)
            items = await self.agent.pubsub.get_items(PUBSUB_JID, TEST_NODE)
            await self.agent.pubsub.delete(PUBSUB_JID, TEST_NODE)
            self.kill(exit_code=items)

    retract_behaviour = RetractBehaviour()
    agent.add_behaviour(retract_behaviour)
    await retract_behaviour.join()
    assert len(retract_behaviour.exit_code) == 0

    await agent.stop()
    assert agent.is_alive() is False
