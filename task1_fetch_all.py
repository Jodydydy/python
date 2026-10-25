"""
Задача 1. Скачать всё, что успеет (заметки 10–12)

Напиши fetch_all(urls, timeout):
- запускает fake_fetch для ВСЕХ url одновременно;
- ждёт не дольше timeout секунд;
- возвращает словарь {url: значение}, где значение:
    * результат fake_fetch, если успел;
    * "error: <текст исключения>", если упал;
    * "timeout", если не успел за timeout;
- те, кто не успел, должны быть ОТМЕНЕНЫ (не оставляй задачи-сироты).

Запуск: python task1_fetch_all.py
"""
import asyncio
import time

# url -> (сколько секунд "качается", результат или исключение)
DATA = {
    "a": (0.2, "A"),
    "b": (0.5, ValueError("boom b")),
    "c": (3.0, "C"),
    "d": (0.1, "D"),
}
CANCELLED = []


async def fake_fetch(url):
    delay, result = DATA[url]
    try:
        await asyncio.sleep(delay)
    except asyncio.CancelledError:
        CANCELLED.append(url)
        raise
    if isinstance(result, Exception):
        raise result
    return result

async def true_fetch(url):
    try:
        return await fake_fetch(url)
    
    
    except Exception as e:
        return f'error: {str(e)}'
 


async def fetch_all(urls, timeout):
    res = {}

    tasks = {url:asyncio.create_task(true_fetch(url)) for url in urls}
    done, pending = await asyncio.wait(tasks.values(), timeout=timeout)



    for k, v in tasks.items():
        if v in pending:
            v.cancel()
            res[k] = 'timeout'
        else:
            res[k] = v.result()

    await asyncio.gather(*pending, return_exceptions=True)
    return res
    ...


# ---------------- проверка, ниже не менять ----------------
async def _check():
    start = time.perf_counter()
    result = await fetch_all(list(DATA), timeout=1)
    elapsed = time.perf_counter() - start
    await asyncio.sleep(0.1)

    expected = {"a": "A", "b": "error: boom b", "c": "timeout", "d": "D"}
    assert result == expected, f"результат:\n  {result}\nожидалось:\n  {expected}"
    assert 0.9 < elapsed < 1.3, f"заняло {elapsed:.2f} с, ожидалось ~1 с (запросы идут одновременно?)"
    assert CANCELLED == ["c"], f"отменены {CANCELLED}, ожидалось ['c'] (не забыл отменить зависших?)"
    print(f"OK ✓  ({elapsed:.2f} с)")


if __name__ == "__main__":
    asyncio.run(_check())
