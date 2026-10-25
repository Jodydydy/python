from random import randrange
import asyncio


async def producer(queue):

    for _ in range(randrange(1, 11)):
        await queue.put(randrange(1, 11))
        await asyncio.sleep(0.1)


async def worker(name, q1, q2):
    print(f'{name} started')

    while True:

        number = await q1.get()

        
        await asyncio.sleep(randrange(1, 3))

        await q2.put(number ** 2)

        q1.task_done()





async def consumer(q):

    while True:
        print(f'result: {await q.get()}')
        q.task_done()


async def main():
    queue = asyncio.Queue(maxsize=10)
    queue2 = asyncio.Queue(maxsize=10)

    p = asyncio.create_task(producer(queue))
    c = asyncio.create_task(consumer(queue2))
    w1 = asyncio.create_task(worker('worker1', queue, queue2))
    w2 = asyncio.create_task(worker('worker2', queue, queue2))

    await p

    await queue.join()
    await queue2.join()

    w1.cancel()
    w2.cancel()
    c.cancel()

    await asyncio.gather(c, w1, w2, return_exceptions=True)


if __name__ == '__main__':
    asyncio.run(main())