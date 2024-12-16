from typing import Optional, List, Union

from slixmpp import ClientXMPP
from slixmpp.exceptions import IqError
from slixmpp.plugins.xep_0004.stanza.form import Form
from slixmpp.plugins.xep_0060 import XEP_0060
from slixmpp.stanza import Iq

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
            self.client: ClientXMPP = client
            self.client.register_plugin('xep_0060')
            self.pubsub: XEP_0060 = self.client['xep_0060']

        # OWNER USE CASES
        async def create(
            self,
            target_jid: str,
            target_node: Optional[str] = None,
            config_form: Optional[Form] = None
        ):
            """
            Create a new node at a service.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str or None): Name of the PubSub node to create
                config_form (Slixmpp Form): Dataform to configurate the node to create
            """
            try:
                return await self.pubsub.create_node(target_jid, target_node, config=config_form)
            except IqError as e:
                logger.error(f"Error creating node <{target_node}>: {e}")

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
                return await self.pubsub.delete_node(target_jid, target_node)
            except IqError as e:
                logger.error(f"Error deleting node <{target_node}>: {e}")

        async def get_node_subscriptions(
            self, target_jid: str, target_node: Optional[str]
        ) -> List[str]:
            """
            Return the subscriptions of other jids with a node.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str): Name of the node to query
            """
            try:
                data: Iq = await self.pubsub.get_node_subscriptions(target_jid, target_node)
                return [sub.attrib.get('jid') for sub in data.get_payload()[0][0]]
            except IqError as e:
                logger.error(f"Error retrieving owner subscriptions from node <{target_node}>: {e}")

        async def purge(self, target_jid: str, target_node: Optional[str]):
            """
            Delete all items from a node.

            Args:
                target_jid (str): JID of the PubSub service
                target_node (str): Name of the PubSub node
            """
            try:
                return await self.pubsub.purge(target_jid, target_node)
            except IqError as e:
                logger.error(f"Error purging node <{target_node}>: {e}")

        async def get_nodes(self, target_jid: str, target_node: Optional[str] = None):
            """
            Request all nodes at a service or collection node.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str or None): Name of the collection node to query
            """
            try:
                res = await self.pubsub.get_nodes(target_jid, target_node)
                return [tostring(item) for item in res.get_payload()[0]]
            except IqError as e:
                logger.error(f"Error deleting node <{target_node}>: {e}")

        async def get_items(self, target_jid: str, target_node: Optional[str]) -> List[str]:
            """
            Request all items at a service or collection node.

            Returns a list of strings, each string representing an <item> element response
            from the server
            Args:
                target_jid (str): Addressof the PubSub service.
                target_node (str): Name of the PubSub node.
            """
            try:
                data: Iq = await self.pubsub.get_items(target_jid, target_node)
                return [tostring(i[0]) for i in data.get_payload()[0][0]]
            except IqError as e:
                logger.error(f"Error retrieving items from node <{target_node}>: {e}")

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
                try:
                    return res, res.get_payload()[0][0].attrib.get('subid')
                except KeyError:
                    return res, None

            except IqError as e:
                logger.error(f"Error subscribing to node <{target_node}>: {e}")

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
                return await self.pubsub.unsubscribe(
                    target_jid,
                    target_node,
                    subscribee=subscription_jid,
                    subid=subid,
                )
            except IqError as e:
                logger.error(f"Error unsubscribing to node <{target_node}>: {e}")

        def set_on_item_published(self, callback):
            self.client.add_event_handler('pubsub_publish', callback)

        def set_on_item_retracted(self, callback):
            self.client.add_event_handler('pubsub_retract', callback)

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
                return await self.pubsub.publish(target_jid, target_node)
            except IqError as e:
                logger.error(f"Error notifying to node <{target_node}>: {e}")

        async def publish(
            self,
            target_jid: str,
            target_node: str,
            payload: str,
            item_id: Optional[str] = None,
        ) -> Union[str, Iq]:
            """
            Publish an item to a node.

            Args:
                target_jid (str): Address of the PubSub service.
                target_node (str): Name of the PubSub node to publish to.
                payload (str): Payload to publish.
                item_id (str or None): Item ID to use for the item.

            Return:
                The response of the server
            """
            try:
                res = await self.pubsub.publish(target_jid, target_node, item_id, payload)
                try:
                    return res.get_payload()[0][0][0].get('id')
                except (IndexError, KeyError):
                    return res
            except IqError as e:
                logger.error(f"Error publishing item <{item_id}> to node <{target_node}>: {e}")

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
                return await self.pubsub.retract(target_jid, target_node, item_id, notify)
            except IqError as e:
                logger.error(f"Error retracting item <{item_id}> to node <{target_node}>: {e}")
