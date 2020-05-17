""" Работа с расходами — их добавление, удаление, статистики"""
import datetime
import re
from typing import List, NamedTuple, Optional

import pytz

import db
import exceptions
from categories import Categories


class Message(NamedTuple):
    """Структура распаршенного сообщения о новом расходе"""
    amount: int
    category_text: str

class Categg(NamedTuple):
    """Структура распаршенного сообщения о новом расходе"""
    name: str
    aliases: str

class Categgg(NamedTuple):
    name: str


class Expense(NamedTuple):
    """Структура добавленного в БД нового расхода"""
    id: Optional[int]
    amount: int
    category_name: str

class Expense2(NamedTuple):
    """Структура добавленного в БД нового расхода"""
    amount: int
    category_name: str

class Expense3(NamedTuple):
    """Структура добавленного в БД нового расхода"""
    dt:str
    category_name: str
    amount: int

def add_expense(raw_message: str,userr_id) -> Expense:
    """Добавляет новое сообщение.
    Принимает на вход текст сообщения, пришедшего в бот."""
    parsed_message = _parse_message(raw_message)
    category = Categories(user_id=userr_id).get_category(
        parsed_message.category_text)
    als=parsed_message.category_text
    inserted_row_id = db.insert("expense", {
        "amount": parsed_message.amount,
        "created": _get_now_formatted(),
        "category_name": category.name,
        "raw_text": raw_message,
        "alias":als,
        "user_id":userr_id
    })

    #ins=str(((userr_id,_get_now_formatted(), parsed_message.amount,category.name,als,raw_message),))[1:-1]

    #cursor = db.get_cursor()
    #cursor.execute(f"insert into expense (user_id,created, amount,category_name,alias,raw_text) values {ins}")

    return Expense(id=None,
                   amount=parsed_message.amount,
                   category_name=category.name)


def get_today_statistics(userr_id) -> List[Expense2]:
    cursor = db.get_cursor()
    cursor.execute(f"select e.alias as name,sum(e.amount) as amount from expense as e where date(e.created)=date('now', 'localtime') and e.user_id={userr_id} group by e.alias")
    rows = cursor.fetchall()
    base_today_expenses = [Expense2(amount=row[1], category_name=row[0]) for row in rows]
    #base_today_expenses = result[0] if result[0] else 0
    return base_today_expenses


def get_today_total(userr_id) -> str:
    cursor = db.get_cursor()
    cursor.execute(f"select sum(amount) from expense where date(created)=date('now', 'localtime') and user_id={userr_id}")
    result = cursor.fetchone()
    all_today_expenses = result[0]
    return all_today_expenses

def get_month_total(userr_id) -> str:
    cursor = db.get_cursor()
    cursor.execute(f"select sum(amount) from expense where strftime('%m',created)=strftime('%m',datetime('now', 'localtime')) and user_id={userr_id}")
    result = cursor.fetchone()
    all_today_expenses = result[0]
    return all_today_expenses

def get_month_statistics(userr_id) -> List[Expense2]:
    cursor = db.get_cursor()
    cursor.execute(f"select c.name,sum(e.amount) as amount from expense e left join category c on e.category_name=c.name where strftime('%m',e.created)=strftime('%m',datetime('now', 'localtime')) and e.user_id={userr_id} group by c.name")
    rows = cursor.fetchall()
    base_today_expenses = [Expense2(amount=row[1], category_name=row[0]) for row in rows]
    #base_today_expenses = result[0] if result[0] else 0
    return base_today_expenses


def get_month_statistics_all(userr_id) -> List[Expense3]:
    cursor = db.get_cursor()
    cursor.execute(f"select strftime('%d-%m-%Y %H:%M',e.created) as dt, e.amount, e.alias as name from expense e where strftime('%m',e.created)=strftime('%m',datetime('now', 'localtime')) and e.user_id={userr_id} order by e.created asc ")
    rows = cursor.fetchall()
    month_expenses = [Expense3(amount=row[1], category_name=row[2],dt=row[0]) for row in rows]
    return month_expenses


def get_month_statistics_graph(userr_id):
    cursor = db.get_cursor()
    cursor.execute(f"select c.name,sum(e.amount) as amount from expense e left join category c on e.category_name=c.name where strftime('%m',e.created)=strftime('%m',datetime('now', 'localtime')) and e.user_id={userr_id} group by c.name")
    rows = cursor.fetchall()
    return rows

def get_month_statistics_graph_by_day(userr_id):
    cursor = db.get_cursor()
    cursor.execute(f"select strftime('%d',e.created) as m,sum(e.amount) as amount from expense e left join category c on e.category_name=c.name where strftime('%m',e.created)=strftime('%m',datetime('now', 'localtime')) and e.user_id={userr_id} group by strftime('%d',e.created)")
    rows = cursor.fetchall()
    return rows

def last(userr_id) -> List[Expense]:
    """Возвращает последние несколько расходов"""
    cursor = db.get_cursor()
    cursor.execute(f"select e.id, e.amount, e.alias as name from expense as e where e.user_id={userr_id} order by e.created desc limit 10")
    rows = cursor.fetchall()
    last_expenses = [Expense(id=row[0], amount=row[1], category_name=row[2]) for row in rows]
    return last_expenses


def delete_expense(row_id: int,userr_id) -> None:
    """Удаляет сообщение по его идентификатору"""
    db.delete("expense", row_id)


def _parse_message(raw_message: str) -> Message:
    """Парсит текст пришедшего сообщения о новом расходе."""
    regexp_result = re.match(r"([\d ]+) (.*)", raw_message)
    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectMessage(
            "Не могу понять сообщение. Напишите сообщение в формате, "
            "например:\n1500 метро")

    amount = regexp_result.group(1).replace(" ", "")
    category_text = regexp_result.group(2).strip().lower()
    return Message(amount=amount, category_text=category_text)


def _get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учётом времненной зоны Мск."""
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz)
    return now

def del_category(raw_message: str,userr_id) -> Categgg:
    ctg=raw_message
    db.delete_ctg("category",str(ctg),userr_id)
    return Categgg(name=ctg)


def add_category(raw_message: str,userr_id) -> Categg:
    ctg=raw_message.split(' ')[0]
    alis=raw_message.split(' ')[1]
    db.insert("category", {
    "name": ctg,
    "aliases":alis,
    "user_id":userr_id})
    return Categg(name=ctg,aliases=alis)

def add_basic_categories(user_id):
    idd=user_id
    
    ins=str(((idd,"продукты_магазы", "пятерочка,перек,магнолия"),
    (idd,"продукты_доставка", "метро,самокат,утконос"),    
    (idd,"сигареты","чапман,сишки,стики"),
    (idd,"кофе", "кофе,какао"),
    (idd,"обед", "столовая"),
    (idd,"еда_доставка", "додо-пицца,бургер-кинг,макдак,суши-стор,достаевский,империя-пицца"),
    (idd,"общ. транспорт", "метро, автобус"),
    (idd,"такси", "яндекс-такси, делимобиль"),
    (idd,"каршеринг","карш")))[1:-1]

    cursor = db.get_cursor()
    cursor.execute(f"insert into category (user_id,name, aliases) values {ins}")
    flag="Базовые категории добавлены!"
    return flag