from random import randrange
import asyncio
import time


async def fetch_source(name):

    await asyncio.sleep(randrange(1, 4))

    return f'data from {name}'


async def collect_data():

    tasks = [fetch_source(f'task{i}') for i in range(1, 6)]

    result = await asyncio.gather(*tasks)

    return result



async def main():
    t0 = time.perf_counter()

    print(await collect_data())

    print(time.perf_counter() - t0)
    


if __name__ == '__main__':
    asyncio.run(main())

