from typing import Optional, List

import slixmpp
from slixmpp.exceptions import IqError
from slixmpp.plugins.xep_0060 import XEP_0060

from loguru import logger
from slixmpp.xmlstream import tostring


class PubSubMixin:
    """
    This mixin provides PubSub support to SPADE agents.
    It must be used as superclass of a spade.Agent subclass.
    """

    async def _hook_plugin_after_connection(self, *args, **kwargs):
        try:
            await super()._hook_plugin_after_connection(*args, **kwargs)
        except AttributeError:
            logger.debug("_hook_plugin_after_connection is undefined")

        self.pubsub = self.PubSubComponent(self.client)

    async def _hook_plugin_before_connection(self, *args, **kwargs):
        """
        Overload this method to hook a plugin before connetion is done
        """
        try:
            await super()._hook_plugin_before_connection(*args, **kwargs)
        except AttributeError:
            logger.debug("_hook_plugin_before_connection is undefined")

    class PubSubComponent:
        def __init__(self, client):
            self.client: slixmpp.ClientXMPP = client
            self.client.register_plugin('xep_0060')
            self.pubsub: XEP_0060 = self.client['xep_0060']

        # OWNER USE CASES

        async def create(self, target_jid: str, target_node: Optional[str] = None):
            """
            Create a new node at a service.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str or None): Name of the PubSub node to create
            """
            try:
                res = await self.pubsub.create_node(target_jid, target_node)
            except IqError as res:
                logger.error(f"Error creating node <{target_node}>: {res}")

            return res

        async def delete(
            self,
            target_jid: str,
            target_node: Optional[str],
        ):
            """
            Delete an existing node.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str or None): Name of the PubSub node to delete.
            """
            try:
                res = await self.pubsub.delete_node(target_jid, target_node)
            except IqError as res:
                logger.error(f"Error deleting node <{target_node}>: {res}")

            return res

        async def get_node_subscriptions(
            self, target_jid: str, target_node: Optional[str]
        ) -> List[str]:
            """
            Return the subscriptions of other jids with a node.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str): Name of the node to query
            """
            data: slixmpp.stanza.Iq = await self.pubsub.get_node_subscriptions(target_jid, target_node)
            return [sub.attrib.get('jid') for sub in data.get_payload()[0][0]]

        async def purge(self, target_jid: str, target_node: Optional[str]):
            """
            Delete all items from a node.

            Args:
                target_jid (str): JID of the PubSub service
                target_node (str): Name of the PubSub node
            """
            try:
                res = await self.pubsub.purge(target_jid, target_node)
            except IqError as res:
                logger.error(f"Error purging node <{target_node}>: {res}")

            return res

        async def get_nodes(self, target_jid: str, target_node: Optional[str] = None):
            """
            Request all nodes at a service or collection node.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str or None): Name of the collection node to query
            """
            try:
                res = await self.pubsub.get_nodes(target_jid, target_node)
                res = [tostring(item) for item in res.get_payload()[0]]
            except IqError as res:
                logger.error(f"Error deleting node <{target_node}>: {res}")

            return res

        async def get_items(self, target_jid: str, target_node: Optional[str]) -> List[str]:
            """
            Request all items at a service or collection node.

            Returns a list of strings, each string representing an <item> element response
            from the server
            Args:
                target_jid (str): Addressof the PubSub service.
                target_node (str): Name of the PubSub node.
                iterator (bool): Bool to enable iterator as returned object
            """
            data: slixmpp.stanza.Iq = await self.pubsub.get_items(target_jid, target_node)
            return [tostring(i[0]) for i in data.get_payload()[0][0]]

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
            try:
                res = await self.pubsub.subscribe(
                    target_jid,
                    target_node,
                    subscribee=subscription_jid,
                    options=config
                )
            except IqError as res:
                logger.error(f"Error subscribing to node <{target_node}>: {res}")

            return res

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
            try:
                res = await self.pubsub.unsubscribe(
                    target_jid,
                    target_node,
                    subscribee=subscription_jid,
                    subid=subid,
                )
            except IqError as res:
                logger.error(f"Error unsubscribing to node <{target_node}>: {res}")

            return res

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
            try:
                res = await self.pubsub.publish(target_jid, target_node)
            except IqError as res:
                logger.error(f"Error notifying to node <{target_node}>: {res}")

            return res

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
            try:
                res = await self.pubsub.publish(target_jid, target_node, item_id, payload)
            except Exception as res:
                logger.error(f"Error publishing item <{item_id}> to node <{target_node}>: {res}")

            return res

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
            try:
                res = await self.pubsub.retract(target_jid, target_node, item_id, notify)
            except IqError as res:
                logger.error(f"Error retracting item <{item_id}> to node <{target_node}>: {res}")

            return res
