=====
Usage
=====

The PubSub plugin gives agents the ability to create nodes, subscribe to nodes and publish items to nodes following the
XEP 0060 (https://xmpp.org/extensions/xep-0060.html).

To use SPADE PubSub in a project::

    from spade_pubsub import PubSubMixin
    from spade import Agent

    class YourAgent(PubSubMixin, Agent):
        # Your code here...

.. warning:: Mixins MUST be always placed before the Agent class in the inheritance order.


Working with nodes
------------------

An agent can create a node where other agents may subscribe in order to receive notifications when new items are published
in such node.

.. warning:: Due to limitations of the XMPP Publish-Subscribe standard, agents MUST be registered in the XMPP server
with creation privileges in order to create nodes. (e.g. In Prosody include them in the admin list (`admins = {}`).


.. tip:: Note that you MUST substitute PUBSUB_JID with the address of the pubsub component that your XMPP server uses (e.g. "pubsub.localhost)


To create and delete a node in a PubSub server::

    await self.agent.pubsub.create(PUBSUB_JID, "Name of the node")
    await self.agent.pubsub.delete(PUBSUB_JID, "Name of the node")


To get all nodes from a PubSub server::

    list_of_nodes = await self.agent.pubsub.get_nodes(PUBSUB_JID)

To purge all items from a node::

       await self.agent.pubsub.purge(PUBSUB_JID, "Name of the node")


Publishing Items to a node
--------------------------

Once a node is created, you can publish information to that node. That information will be received by all subscriptors of the node.

Publish an item::

        await self.agent.pubsub.publish(PUBSUB_JID, "Name of the node", "Payload of the item")

Get all published items from a node::

        items = await self.agent.pubsub.get_items(PUBSUB_JID, "Name of the node")


Subscribe and unsubscribe::

            await self.agent.pubsub.subscribe(PUBSUB_JID, "Name of the node")
            await self.agent.pubsub.unsubscribe(PUBSUB_JID, "Name of the node")


Register callback function to receive published items::

        def my_callback(self, jid, node, item, message=None):
            # Your code here

        # register callback
        self.agent.pubsub.set_on_item_published(my_callback)


Get all subscriptions of a node::

            list_of_subs = await self.agent.pubsub.get_node_subscriptions(PUBSUB_JID, "Name of the node")


