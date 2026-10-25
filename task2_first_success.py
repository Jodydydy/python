"""
Задача 2. Первый УСПЕШНЫЙ ответ (заметки 10–11)

Спрашиваем несколько серверов. Некоторые отвечают ошибкой.
Напиши first_success(servers):
- опрашивает все серверы одновременно;
- возвращает имя сервера, который ПЕРВЫМ ответил УСПЕШНО
  (быстрая ошибка не считается — ждём дальше);
- как только есть успешный ответ — остальные отменить;
- если упали все — выбросить RuntimeError("all failed").

Подсказка: подумай, чем тут плох FIRST_COMPLETED в один вызов.

Запуск: python task2_first_success.py
"""
import asyncio
import time

CANCELLED = []


async def ask(name, delay, ok):
    try:
        await asyncio.sleep(delay)
    except asyncio.CancelledError:
        CANCELLED.append(name)
        raise
    if not ok:
        raise ConnectionError(f"{name} недоступен")
    return name


async def first_success(servers):
    """servers: {имя: (задержка, ok)}"""
    tasks = [asyncio.create_task(ask(name, value[0], value[1])) for name, value in servers.items()]

    pending = tasks

    while pending:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

        for t in done:
            if t.exception() is None:
                for c in pending:
                    c.cancel()
                return t.result()

      
    raise RuntimeError("all failed")


# ---------------- проверка, ниже не менять ----------------
async def _check():
    servers = {
        "nyc": (0.1, False),
        "msk": (0.3, False),
        "fra": (0.5, True),
        "tok": (0.8, True),
        "syd": (1.5, True),
    }
    start = time.perf_counter()
    winner = await first_success(servers)
    elapsed = time.perf_counter() - start
    await asyncio.sleep(0.05)
    assert winner == "fra", f"победил {winner!r}, ожидался 'fra'"
    assert 0.45 < elapsed < 0.7, f"заняло {elapsed:.2f} с, ожидалось ~0.5 с"
    assert sorted(CANCELLED) == ["syd", "tok"], f"отменены {CANCELLED}, ожидались tok и syd"

    CANCELLED.clear()
    try:
        await first_success({"x": (0.1, False), "y": (0.2, False)})
    except RuntimeError as e:
        assert str(e) == "all failed", f"текст ошибки: {e!r}"
    else:
        raise AssertionError("когда все упали, должен быть RuntimeError('all failed')")
    print(f"OK ✓  ({elapsed:.2f} с)")


if __name__ == "__main__":
    asyncio.run(_check())
