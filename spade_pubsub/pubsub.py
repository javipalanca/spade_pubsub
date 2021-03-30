import aioxmpp


class PubSubMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pubsub = self.client.summon(aioxmpp.PubSubClient)

    def set_on_item_published(self, callback):
        self.pubsub.on_item_published.connect(callback)

    def set_on_item_retracted(self, callback):
        self.pubsub.on_item_retracted.connect(callback)

    async def subscribe(self, target_entity, target_node):
        subid = (await self.pubsub.subscribe(
            target_entity,
            node=target_node,
        )).payload.subid

        return subid

    async def unsubscribe(self, target_entity, target_node, subid):
        await self.pubsub.unsubscribe(
            target_entity,
            node=target_node,
            subid=subid,
        )

    async def get_nodes(self, target_entity):
        return await self.pubsub.get_nodes(target_entity)

    async def get_items(self, target_entity, target_node):
        return await self.pubsub.get_items(target_entity, node=target_node)
