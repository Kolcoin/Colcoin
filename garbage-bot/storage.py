"""Хранилище заявок в памяти.

Это MVP — данные живут только пока бот запущен. После рестарта — пустота.

TODO: заменить на БД (SQLite через aiosqlite или Postgres через asyncpg).
Структура таблицы orders уже видна по полям dict ниже —
останется только перенести её в схему и переписать функции
create_order / get_order / mark_done на async-запросы.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Order:
    id: int
    client_chat_id: int
    client_username: Optional[str]
    bags: int
    price: int
    address: str
    status: str = "new"  # new -> in_progress -> done
    courier_chat_id: Optional[int] = None


# Ключ — id заказа, значение — Order.
_orders: dict[int, Order] = {}
_next_id: int = 1


def create_order(
    *,
    client_chat_id: int,
    client_username: Optional[str],
    bags: int,
    price: int,
    address: str,
) -> Order:
    global _next_id
    order = Order(
        id=_next_id,
        client_chat_id=client_chat_id,
        client_username=client_username,
        bags=bags,
        price=price,
        address=address,
    )
    _orders[_next_id] = order
    _next_id += 1
    return order


def get_order(order_id: int) -> Optional[Order]:
    return _orders.get(order_id)


def mark_in_progress(order_id: int, courier_chat_id: int) -> Optional[Order]:
    order = _orders.get(order_id)
    if order is None:
        return None
    order.status = "in_progress"
    order.courier_chat_id = courier_chat_id
    return order


def mark_done(order_id: int) -> Optional[Order]:
    order = _orders.get(order_id)
    if order is None:
        return None
    order.status = "done"
    return order


# ============================================================================
# TODO: ЗДЕСЬ БУДЕТ ПОЛЬЗОВАТЕЛЬСКАЯ ИСТОРИЯ И ПОДПИСКИ
# ----------------------------------------------------------------------------
# Когда заведём БД — добавим таблицу users со счётчиком абонемента,
# историей заказов и статусом подписки. Сейчас намеренно не делаем.
# ============================================================================
