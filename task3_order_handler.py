"""
Задача 3. Обработчик заказа (заметки 12–14)

Есть веб-сервер на asyncio. Пока он работает, heartbeat() каждые 0.1 с
отмечается "я жив" — если цикл событий заблокирован, отметок не будет.

Напиши handle_order(order_id), которая:
1. Формирует чек через СТАРУЮ БЛОКИРУЮЩУЮ функцию render_receipt (0.3 с).
   Цикл событий при этом блокироваться не должен.
2. Сохраняет заказ через save_order (занимает 1 с).
   Пользователь не должен ждать сохранения дольше 0.5 с:
   - успели — вернуть "saved";
   - не успели — вернуть "processing", НО сохранение обязано дойти до конца
     (отменять его нельзя — получится полузаписанный заказ).

Менять render_receipt и save_order нельзя.

Запуск: python task3_order_handler.py
"""
import asyncio
import time

SAVED = []
BROKEN = []


def render_receipt(order_id):          # старая синхронная библиотека
    time.sleep(0.3)
    return f"receipt-{order_id}"


async def save_order(order_id):
    try:
        await asyncio.sleep(1)
        SAVED.append(order_id)
    except asyncio.CancelledError:
        BROKEN.append(order_id)
        raise


async def handle_order(order_id):
    await asyncio.to_thread(render_receipt, order_id)
    task = asyncio.create_task(save_order(order_id))


    try:
        await asyncio.wait_for(asyncio.shield(task), timeout=0.5)
    except TimeoutError:
        return 'processing'    

    return 'saved'




# ---------------- проверка, ниже не менять ----------------
async def _check():
    ticks = 0

    async def heartbeat():
        nonlocal ticks
        while True:
            await asyncio.sleep(0.1)
            ticks += 1

    hb = asyncio.create_task(heartbeat())
    start = time.perf_counter()
    answers = await asyncio.gather(*(handle_order(i) for i in range(5)))
    elapsed = time.perf_counter() - start
    await asyncio.sleep(1)
    hb.cancel()

    assert answers == ["processing"] * 5, f"ответы: {answers}"
    assert elapsed < 1.0, f"пользователи ждали {elapsed:.2f} с — дольше, чем нужно (чеки формируются одновременно?)"
    assert not BROKEN, f"сохранение заказов {BROKEN} было прервано!"
    assert sorted(SAVED) == list(range(5)), f"сохранены {SAVED}, ожидались все 5"
    assert ticks >= 15, f"heartbeat отметился {ticks} раз — цикл событий блокировался"
    print(f"OK ✓  (ответ за {elapsed:.2f} с, heartbeat {ticks} раз)")


if __name__ == "__main__":
    asyncio.run(_check())
