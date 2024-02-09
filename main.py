import os
import subprocess

import telebot
from dotenv import load_dotenv

from pdf_creation import create_pdf
from send_pdf_to_print import send_pdf_to_print

load_dotenv()
TG_BOT_TOKEN = os.getenv("TG_TOKEN")
MY_TELEGRAM_ID = int(os.getenv("MY_TELEGRAM_ID"))
WIFE_TELEGRAM_ID = int(os.getenv("WIFE_TELEGRAM_ID"))
# default_printer_name = os.getenv("DEFAULT_PRINTER")

allowed_users = (MY_TELEGRAM_ID, WIFE_TELEGRAM_ID)

bot = telebot.TeleBot(TG_BOT_TOKEN)

path_to_file = ""


def pages_per_sheet_keyboard() -> telebot.types.InlineKeyboardMarkup:
    return telebot.types.InlineKeyboardMarkup(
        keyboard=[
            [
                telebot.types.InlineKeyboardButton(text="1", callback_data="1pps"),
                telebot.types.InlineKeyboardButton(text="2", callback_data="2pps"),
                telebot.types.InlineKeyboardButton(text="4", callback_data="4pps"),
            ],
        ],
    )


def print_mode_keyboard() -> telebot.types.InlineKeyboardMarkup:
    return telebot.types.InlineKeyboardMarkup(
        row_width=1,
        keyboard=[
            [telebot.types.InlineKeyboardButton(text="Односторонняя", callback_data="simplex")],
            [telebot.types.InlineKeyboardButton(text="Двусторонняя по длинному краю", callback_data="duplexlong")],
            [telebot.types.InlineKeyboardButton(text="Двусторонняя по короткому краю", callback_data="duplexshort")],
        ],
    )


@bot.message_handler(func=lambda msg: msg.text == "Мяу")
def print_user_id(message):
    print(message.from_user.id)


@bot.message_handler(content_types=["document"])
@bot.message_handler(func=lambda msg: msg.from_user.id in allowed_users)
def save_file(message):
    global path_to_file

    downloaded_file = bot.download_file(bot.get_file(message.document.file_id).file_path)
    path_to_file = ".\\docs_to_print\\" + message.document.file_name

    with open(path_to_file, "wb") as new_file:
        new_file.write(downloaded_file)

    print(f"Downloaded the file {path_to_file}")

    file_extension = path_to_file.split(".")[-1]
    if file_extension == "docx":
        final_path = ".".join(path_to_file.split(".")[:-1]) + ".pdf"
        subprocess.run(["docx2pdf", path_to_file], check=True)
        path_to_file = final_path
    elif file_extension == "pdf":
        pass
    else:
        bot.send_message(message.chat.id, "Такое я печатать не умею :(")
        return

    bot.reply_to(message, "Сколько страниц на листе?", reply_markup=pages_per_sheet_keyboard())
    bot.send_message(message.chat.id, "Какая печать?", reply_markup=print_mode_keyboard())


@bot.callback_query_handler(func=lambda call: call.data in {"1pps", "2pps", "4pps"})
def callback_for_pps(call):
    global path_to_file

    print(f"User asked for {call.data[0]} pages per sheet")

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.edit_message_text(
        text=call.message.text + f"\n{call.data[0]}",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )
    if call.data == "1pps":
        print("1pps, nothing to do")
    else:
        path_to_file = create_pdf(path_to_file, pages_per_sheet=int(call.data[0]))


@bot.callback_query_handler(func=lambda call: call.data in {"simplex", "duplexlong", "duplexshort"})
def callback_of_print_mode(call):
    print(f"User asked for {call.data}")

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.edit_message_text(
        text=call.message.text + f"\n{call.data}",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )
    print_mode = str(call.data)
    send_pdf_to_print(path_to_file, mode=print_mode)


bot.infinity_polling()
