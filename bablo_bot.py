"""Сервер Telegram бота, запускаемый непосредственно"""
#import logging
import os
import exceptions
import expenses
from categories import Categories
import  graphics
import datetime
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
#logging.basicConfig(level=logging.INFO)

TOKEN=os.getenv("TELEGRAM_API_TOKEN")
PROXY_URL=os.getenv("TELEGRAM_PROXY_URL")
bot = Bot(token=TOKEN,proxy=PROXY_URL)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(
    	"Добавить базовые категории: /add_basic_categories\n"
        "Категории трат: /categories\n"
        "Добавить расход: 250 такси\n"
        "За сегодня: /today\n"
        "За текущий месяц по категориям: /month\n"
        "За текущий месяц все покупки: /month_detail\n"
        "За текущий месяц график: /month_graph\n"
        "Последние внесённые расходы: /expenses\n"
        "Добавить категорию c группами: /addctg кайфы пиво,чипсы\n"
        "Удалить категорию: /dltctg кайфы\n"
        )

@dp.message_handler(commands=['add_basic_categories'])
async def add_categories_list(message: types.Message):
    """Отправляет список категорий расходов"""
    usr_id=int(message.from_user.id)
    result = expenses.add_basic_categories(usr_id)
    answer_message = result
    await message.answer(answer_message)



@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
    """Удаляет одну запись о расходе по её идентификатору"""
    row_id = int(message.text[4:])
    expenses.delete_expense(row_id)
    answer_message = "Удалил"
    await message.answer(answer_message)


@dp.message_handler(commands=['categories'])
async def categories_list(message: types.Message):
    """Отправляет список категорий расходов"""
    usr_id=int(message.from_user.id)
    categories = Categories(user_id=usr_id).get_all_categories()
    answer_message = "Категории(группы) трат:\n\n* " +\
            ("\n\n* ".join([c.name+' ('+", ".join(c.aliases)+')' for c in categories]))
    await message.answer(answer_message)

@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    """Отправляет сегодняшнюю статистику трат"""
    usr_id=int(message.from_user.id)
    answer_message = expenses.get_today_statistics(usr_id)
    if not answer_message:
        await message.answer("Сегодня мы не просадили ни рубля:)")
        return    
    total=expenses.get_today_total(usr_id)

    today_expenses_rows = [
        f"{expense.amount} руб. на {expense.category_name}"
        for expense in answer_message]
    answer_message = "Сегодня мы потратили: "+str(total)+" руб \n\n* " + "\n\n* ".join(today_expenses_rows)
    await message.answer(answer_message)


@dp.message_handler(commands=['month'])
async def month_statistics(message: types.Message):
    usr_id=int(message.from_user.id)
    answer_message = expenses.get_month_statistics(usr_id)
    if not answer_message:
        await message.answer("За весь месяц мы не просадили ни рубля:)")
        return    
    total=expenses.get_month_total(usr_id)

    month_expenses_rows = [
        f"{expense.amount} руб. на {expense.category_name}"
        for expense in answer_message]
    answer_message = "За месяц мы потратили:  "+str(total)+" руб \n\n* " + "\n\n* ".join(month_expenses_rows)
    await message.answer(answer_message)


@dp.message_handler(commands=['month_graph'])
async def month_statistics(message: types.Message):
    usr_id=int(message.from_user.id)
    answer_message = expenses.get_month_statistics(usr_id)
    if not answer_message:
        await message.answer("За весь месяц мы не просадили ни рубля:)")
        return    
    total=expenses.get_month_total(usr_id)

    month_expenses_rows = [
        f"{expense.amount} руб. на {expense.category_name}"
        for expense in answer_message]
    answer_message = "За месяц мы потратили:  "+str(total)+" руб \n\n"

    result=expenses.get_month_statistics_graph(usr_id)
    vals=[i[-1] for i in result]
    labels=[i[0] for i in result]
    plt=graphics.month_graph(vals,labels)

    result_by_day=expenses.get_month_statistics_graph_by_day(usr_id)
    vals=[i[-1] for i in result_by_day]
    dt=[int(i[0].replace('0','')) if i[0].split('0')[0]=='' else  int(i[0]) for i in result_by_day]
    min_dt=min(dt)
    max_dt=max(dt)
    dt_add=[i for i in range(1,min_dt)]
    vals_add=[0 for i in range(1,min_dt)]
    dt_add.extend(dt)
    vals_add.extend(vals)
    dt=dt_add
    vals=vals_add

    curr_day=datetime.datetime.now().day
    if max_dt<curr_day:
        dt_add_fut=[i for i in range(max_dt+1,curr_day+1)]
        val_add_fut=[0 for i in range(max_dt+1,curr_day+1)]
        dt.extend(dt_add_fut)
        vals.extend(val_add_fut)
    plt_by_day=graphics.month_graph_by_day(dt,vals)

    await message.answer(answer_message)
    with open(plt, 'rb') as photo:
        await message.reply_photo(photo)
    with open(plt_by_day, 'rb') as photo:
        await message.reply_photo(photo)


@dp.message_handler(commands=['month_detail'])
async def month_statistics_detail(message: types.Message):
    usr_id=int(message.from_user.id)
    answer_message = expenses.get_month_statistics_all(usr_id)
    if not answer_message:
        await message.answer("За весь месяц мы не просадили ни рубля:)")
        return    
    total=expenses.get_month_total(usr_id)

    month_expenses_rows = [
        f"{expense.dt}   {expense.amount} руб.  на  {expense.category_name}"
        for expense in answer_message]
    answer_message = "За месяц мы потратили:  "+str(total)+" руб \n\n* " + "\n\n* ".join(month_expenses_rows)
    await message.answer(answer_message)



@dp.message_handler(commands=['expenses'])
async def list_expenses(message: types.Message):
    """Отправляет последние несколько записей о расходах"""
    usr_id=int(message.from_user.id)
    last_expenses = expenses.last(usr_id)
    if not last_expenses:
        await message.answer("Расходы ещё не заведены")
        return

    last_expenses_rows = [
        f"{expense.amount} руб. на {expense.category_name} — нажми "
        f"/del{expense.id} для удаления"
        for expense in last_expenses]
    answer_message = "Последние сохранённые траты:\n\n* " + "\n\n* "\
            .join(last_expenses_rows)
    await message.answer(answer_message)

@dp.message_handler(lambda message: message.text.startswith('/addctg'))
async def add_ctg(message: types.Message):
    usr_id=int(message.from_user.id)
    categ = message.text[8:]
    added=expenses.add_category(categ,usr_id)
    answer_message = (
        f"Добавлена категория: {added.name}\n с группами: {added.aliases}.\n")
    await message.answer(answer_message)

@dp.message_handler(lambda message: message.text.startswith('/dltctg'))
async def del_ctg(message: types.Message):
    usr_id=int(message.from_user.id)
    categ = message.text[8:]
    deled=expenses.del_category(categ,usr_id)
    answer_message = (
        f"Удалена категория: {deled.name}\n")
    await message.answer(answer_message)

@dp.message_handler()
async def add_expense(message: types.Message):
    """Добавляет новый расход"""
    usr_id=int(message.from_user.id)
    try:
        expense = expenses.add_expense(message.text,usr_id)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    answer_message = (
        f"Добавлены траты {expense.amount} руб на {expense.category_name}.\n\n")
    await message.answer(answer_message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
