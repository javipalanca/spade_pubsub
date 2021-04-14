from typing import Optional, List

import aioxmpp
import aioxmpp.pubsub.xso as pubsub_xso
from aioxmpp import JID


class PubSubMixin:
    """
    This mixin provides PubSub support to SPADE agents.
    It must be used as superclass of a spade.Agent subclass.
    """

    async def _hook_plugin_after_connection(self, *args, **kwargs):
        super()._hook_plugin_after_connection(*args, **kwargs)
        self.pubsub = self.PubSubComponent(self.client)

    class PubSubComponent:
        def __init__(self, client):
            self.client = client
            self.pubsub = self.client.summon(aioxmpp.PubSubClient)

        # OWNER USE CASES

        async def create(self, target_jid: str, target_node: Optional[str] = None):
            """
            Create a new node at a service.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str or None): Name of the PubSub node to create
            """
            target_jid = JID.fromstr(target_jid)
            return await self.pubsub.create(target_jid, target_node)

        async def delete(
            self,
            target_jid: str,
            target_node: Optional[str],
            redirect_uri: Optional[str] = None,
        ):
            """
            Delete an existing node.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str or None): Name of the PubSub node to delete.
                redirect_uri (str or None): A URI to send to subscribers to indicate a replacement for the deleted node."""
            target_jid = JID.fromstr(target_jid)
            return await self.pubsub.delete(
                target_jid, target_node, redirect_uri=redirect_uri
            )

        async def get_node_subscriptions(
            self, target_jid: str, target_node: Optional[str]
        ) -> List[str]:
            """
            Return the subscriptions of other jids with a node.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str): Name of the node to query
            """
            target_jid = JID.fromstr(target_jid)
            result = await self.pubsub.get_node_subscriptions(target_jid, target_node)
            return [str(x.jid) for x in result.payload.subscriptions]

        async def purge(self, target_jid: str, target_node: Optional[str]):
            """
            Delete all items from a node.

            Args:
                target_jid (str): JID of the PubSub service
                target_node (str): Name of the PubSub node
            """
            target_jid = JID.fromstr(target_jid)
            return await self.pubsub.purge(target_jid, target_node)

        async def get_nodes(self, target_jid: str, target_node: Optional[str] = None):
            """
            Request all nodes at a service or collection node.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str or None): Name of the collection node to query
            """
            target_jid = JID.fromstr(target_jid)
            return await self.pubsub.get_nodes(target_jid, target_node)

        async def get_items(self, target_jid: str, target_node: Optional[str]):
            """
            Request all items at a service or collection node.

            Args:
                target_jid (str): Addressof the PubSub service.
                target_node (str): Name of the PubSub node.
            """
            target_jid = JID.fromstr(target_jid)
            request = await self.pubsub.get_items(target_jid, node=target_node)
            return [item.registered_payload.TAG[1] for item in request.payload.items]

        # SUBSCRIBER USE CASES

        async def subscribe(
            self,
            target_jid: str,
            target_node: Optional[str] = None,
            subscription_jid: Optional[str] = None,
            config=None,
        ):
            """
            Subscribe to a node.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str): Name of the PubSub node to subscribe to.
                subscription_jid (str): The address to subscribe to the service.
                config (Data): Optional configuration of the subscription
            """
            target_jid = JID.fromstr(target_jid)
            subscription_jid = (
                JID.fromstr(subscription_jid) if subscription_jid is not None else None
            )
            return await self.pubsub.subscribe(
                target_jid,
                target_node,
                subscription_jid=subscription_jid,
                config=config,
            )

        async def unsubscribe(
            self,
            target_jid: str,
            target_node: Optional[str] = None,
            subscription_jid: Optional[str] = None,
            subid=None,
        ):
            """
            Unsubscribe from a node.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str): Name of the PubSub node to unsubscribe from.
                subscription_jid (str): The address to subscribe from the service.
                subid (str): Unique ID of the subscription to remove.
            """
            target_jid = JID.fromstr(target_jid)
            subscription_jid = (
                JID.fromstr(subscription_jid) if subscription_jid is not None else None
            )
            return await self.pubsub.unsubscribe(
                target_jid, target_node, subscription_jid=subscription_jid, subid=subid
            )

        def set_on_item_published(self, callback):
            self.pubsub.on_item_published.connect(callback)

        def set_on_item_retracted(self, callback):
            self.pubsub.on_item_retracted.connect(callback)

        # PUBLISHER USE CASES

        async def notify(self, target_jid: str, target_node: str):
            """
            Notify all subscribers of a node without publishing an item.
            “Publish” to the node at jid without any item. This merely fans out a notification.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str): Name of the PubSub node to send a notify from.
            """
            target_jid = JID.fromstr(target_jid)
            return await self.pubsub.notify(target_jid, target_node)

        async def publish(
            self,
            target_jid: str,
            target_node: str,
            payload: str,
            item_id: Optional[str] = None,
        ):
            """
            Publish an item to a node.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str): Name of the PubSub node to publish to.
                payload (str): Payload to publish.
                item_id (str or None): Item ID to use for the item.
            """
            target_jid = JID.fromstr(target_jid)

            @pubsub_xso.as_payload_class
            class SpadePayload(aioxmpp.xso.XSO):
                TAG = "spade.pubsub", payload

            return await self.pubsub.publish(
                target_jid, target_node, SpadePayload(), id_=item_id
            )

        async def retract(
            self, target_jid: str, target_node: str, item_id: str, notify=False
        ):
            """
            Retract a previously published item from a node.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str): Name of the PubSub node to send a notify from.
                item_id (str): The ID of the item to retract.
                notify (bool): Flag indicating whether subscribers shall be notified about the retraction.
            """
            target_jid = JID.fromstr(target_jid)
            return await self.pubsub.retract(
                target_jid, target_node, item_id, notify=notify
            )
