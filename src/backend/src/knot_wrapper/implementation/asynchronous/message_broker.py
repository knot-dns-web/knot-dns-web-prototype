
import asyncio
import redis.asyncio as redis

class DNSWorker:
    def __init__(
        self,
        redis: redis.Redis,
        channel: str,
        socket_path: str
    ) -> None:
        self._redis = redis
        self._socket_path = socket_path 
        self._channel = channel

    async def run(self):
        async with self._redis.pubsub() as pubsub:
            await pubsub.subscribe(self._channel)
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    text = message['data'].decode('utf-8')
                    print(text)

class DNSTaskProducer:
    def __init__(
        self,
        redis: redis.Redis,
        channel: str
    ) -> None:
        self._redis = redis
        self._channel = channel

    async def enqueue_task(self, task: str):
        await self._redis.publish(self._channel, task)