import json
from time import sleep
import threading
import requests
from app import flask_app
from app.models import *
from flask import request
from app import db
from app.config import *
from app.menu import *

data = {"url": WEBHOOK_URL}
url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/setWebHook"

requests.post(url, data)


def working_loop():
    while True:
        sleep(60)
        users = User.query.all()
        for user in users:

            income = 0
            for worker in user.gold_mine.diggers:
                income += worker.income * worker.count
            user.balance_rubles += income
        db.session.commit()


@flask_app.route("/", methods=["POST"])
def receive():
    if "callback_query" in request.json:
        processing_button()
    if "message" in request.json:
        if "game" in request.json["message"]:
            return "OK"
        if "text" in request.json["message"]:

            user_id = request.json["message"]["from"]["id"]
            username = request.json["message"]["from"]["username"]
            user = User.query.get(int(user_id))
            chat_id = request.json["message"]["chat"]["id"]
            message_id = request.json["message"]["message_id"]

            if user is None:

                if request.json["message"]["text"] == "/start":
                    user = User(id=int(user_id), username=username, balance_rubles=0, balance_dollars=0)
                    gold_mine = GoldMine(user_id=user_id)
                    db.session.add(user)

                    db.session.commit()
                    db.session.add(gold_mine)
                    db.session.commit()
                    worker = Digger(gold_mine_id=gold_mine.id, income=100, name="😩 You", count=1, price=5)
                    db.session.add(Digger(price=digger1_worker.price, income=digger1_worker.income,
                                          gold_mine_id=user.gold_mine.id, name=digger1_worker.name, count=0))
                    db.session.add(Digger(price=digger2_worker.price, income=digger2_worker.income,
                                          gold_mine_id=user.gold_mine.id, name=digger2_worker.name, count=0))
                    db.session.add(worker)

                    db.session.commit()
                    create_menu(user_id, main_menu(), "Main menu")
                else:
                    send_message(
                        "Welcome to Gold Mine. Write /start to start",
                        user_id)
            else:

                if user.menu is None:
                    create_menu(user_id, main_menu(), "Main Menu")

                elif user.menu == "Balance":
                    create_menu(user_id, balance_menu(), balance_text(user))

                elif user.menu == "Workers":
                    create_menu(user_id, workers_menu(), get_workers())

                elif user.menu == "GoldMine":
                    create_menu(user_id, goldmine_menu(), workers_to_string(user.gold_mine.diggers))

                elif user.menu == "MainMenu":
                    create_menu(user_id, main_menu(), "Main Menu")

            delete_message(chat_id, message_id)

    return "GOOD"


def create_menu(user_id, menu, message):
    headers = {"Content-type": "application/json"}
    data = {"chat_id": user_id, "text": message}
    data.update(menu)
    data = json.dumps(data)
    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, headers=headers, data=data)


def create_button(message, user_id, callback_data):
    headers = {"Content-type": "application/json"}
    data = {"chat_id": user_id,
            "text": message,
            "reply_markup": {"inline_keyboard":
                                 [[{"text": "nig", "callback_data": callback_data}]]}}

    data = json.dumps(data)
    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(url, headers=headers, data=data)
    print(res)
    pass


def delete_message(chat_id, message_id):

    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/deleteMessage"
    data = {"chat_id": chat_id, "message_id": message_id}
    requests.post(url, data=data)


def edit_message(message, chat_id, message_id, menu):
    data = {"chat_id": chat_id, "message_id": message_id, "text": message}
    data.update(menu)
    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/editMessage"
    requests.post(url, data=data)


def send_message(message, user_id):
    data = {"chat_id": user_id, "text": message}
    url = f"{TELEGRAM_URL}/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data=data)


def workers_to_string(workers):

    text = "Your workers:\n"
    income = 0
    i = 1
    for worker in workers:
        income += worker.income * worker.count
        if worker.count != 0:
            text += f"{i}. {worker.name}\n💰 income: {worker.income},\n count: {worker.count}.\n"
            i += 1
    text += f"Total income: {income}"
    return text


def balance_text(user):

    return f"Balance rubles BYN: {user.balance_rubles:.2f},"f" \nBalance dollars 💸: {user.balance_dollars:.2f}"


def processing_button():

    user_id = request.json["callback_query"]["from"]["id"]
    chat_id = request.json["callback_query"]["message"]["chat"]["id"]
    message_id = request.json["callback_query"]["message"]["message_id"]
    user = User.query.get(int(user_id))
    rdata = request.json["callback_query"]["data"]

    # view rubles and dollar balance
    if rdata == "Balance":

        user.menu = "Balance"
        create_menu(user_id, balance_menu(), balance_text(user))

    # view all workers on car wash
    elif rdata == "Workers":

        user.menu = "Workers"
        create_menu(user_id, workers_menu(), get_workers())

    # button of goldmine in main menu
    elif rdata == "GoldMine":

        user.menu = "GoldMine"
        create_menu(user_id, goldmine_menu(), workers_to_string(user.gold_mine.diggers))

    # Button of returning to main menu
    elif rdata == "BackMenu":

        user.menu = "MainMenu"
        create_menu(user_id, main_menu(), "Main menu")

    # button exchange rubles in balance menu
    elif rdata == "ExchangeRubles":
        rates = requests.get("https://www.nbrb.by/api/exrates/rates/145")
        user.balance_dollars += user.balance_rubles / rates.json()["Cur_OfficialRate"]
        user.balance_rubles = 0
        db.session.commit()
        create_menu(user_id, balance_menu(), balance_text(user))

    # Buying some worker
    elif "BuyWorker" in rdata:

        if rdata.endswith("1"):
            buy_worker("👷 Digger lvl.1", user)
        elif rdata.endswith("2"):
            buy_worker("👷 Digger lvl.2", user)

        create_menu(user_id, workers_menu(), get_workers())
        db.session.commit()
    elif "RechargeBalance" in rdata:

        return

    delete_message(chat_id, message_id)
    db.session.commit()


def get_workers():
    return "You can buy diggers to work on your Gold Mine\n" f"1.{digger1_worker.name}\n\t--💵 Price - " \
           f"{digger1_worker.price}💸\n\t"    f"--Income per minute - {digger1_worker.income} BYN\n" \
           f"2.{digger2_worker.name}\n\t--💵 Price - {digger2_worker.price}💸\n\t" \
           f"--Income per minute - {digger2_worker.income} BYN"


def buy_worker(name, user):
    if user.balance_dollars < digger1_worker.price:
        send_message("Please donate dollars or exchange them", user.id)
    else:
        for worker in user.gold_mine.diggers:
            if worker.name == name:
                user.balance_dollars -= digger1_worker.price
                worker.count += 1
                break


x = threading.Thread(target=working_loop)
x.start()
flask_app.run()
