from app import Digger


def workers_menu():
    return {
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "BackMenu"}],
                                                 [{"text": "1", "callback_data": "BuyWorker1"},
                                                  {"text": "2", "callback_data": "BuyWorker2"}]]}}


def main_menu():
    return {"text": "Main Menu",
            "reply_markup": {"inline_keyboard": [[{"text": "💰 Balance", "callback_data": "Balance"},
                                                  {"text": "👷 Diggers", "callback_data": "Workers"}],
                                                 [{"text": "⛏️Gold Mine", "callback_data": "GoldMine"}]]}}


def goldmine_menu():
    return {
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "BackMenu"}]]}}


def balance_menu():
    return {
            "reply_markup": {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "BackMenu"},
                                                  {"text": "₽➡️💸 Exchange Rubles", "callback_data": "ExchangeRubles"}],

                                                 [{"text": "Recharge balance(в разработке)", "callback_data": "RechargeBalance"}]]}}


digger1_worker = Digger(price=10, income=1, name="👷 Digger lvl.1")
digger2_worker = Digger(price=100, income=12, name="👷 Digger lvl.2")

