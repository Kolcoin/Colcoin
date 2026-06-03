"""Хранилище заявок в памяти.

MVP: после рестарта данные исчезают.

TODO: заменить на БД (SQLite через aiosqlite или Postgres через asyncpg).
Структура полей Order ниже = будущая схема таблицы orders.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Order:
    id: int
    client_chat_id: int          # личный чат клиента с ботом
    client_user_id: int
    client_username: Optional[str]
    client_name: str
    day: str                     # "Сегодня" / "Завтра"
    time: str                    # "🌅 Утро ..." / "🌆 Вечер ..."
    bags: int
    address: str
    phone: str
    price: int
    courier_pay: int
    status: str = "awaiting_payment"  # awaiting_payment / paid / assigned / waiting_photo / done


_orders: dict[int, Order] = {}
_next_id: int = 1


def create_order(**fields) -> Order:
    global _next_id
    order = Order(id=_next_id, **fields)
    _orders[_next_id] = order
    _next_id += 1
    return order


def get_order(order_id: int) -> Optional[Order]:
    return _orders.get(order_id)


def set_status(order_id: int, status: str) -> Optional[Order]:
    order = _orders.get(order_id)
    if order is not None:
        order.status = status
    return order
