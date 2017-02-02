from telegram.ext import MessageHandler, Filters
from telegram.ext import CommandHandler
from telegram.ext import Updater
import os.path
import sys
import time
import logging
from time import gmtime, strftime
import pyotp
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

debug = False

config_file = ".token_secret"
my_token = None
if os.path.isfile(config_file):
    with open (config_file, "r") as my_config:
        my_token=my_config.read(100)

if my_token is None:
    print("Couldn't find any token")
    sys.exit(1)

updater = Updater(token=my_token)
dispatcher = updater.dispatcher

if os.path.isfile("config.json"):
    valid_uids = json.load(open("config.json"))
    # print(valid_uids)
else:
# Testing purposes
    valid_uids = {
        11617294: {
            "name": "DRoBeR",
            "phone": "+34XXXXXXXXX"
        }
    }


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Hola, Dragonico. Aquí me tienes. Cuéntame tus penas!")
    print("chat_id: {}".format(update.message.chat_id))

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def open_door(bot, update):
    chat_id = update.message.chat_id
    if update.message.chat_id in valid_uids:
        username = valid_uids[update.message.chat_id]['name']
        bot.sendMessage(chat_id=chat_id, text="Para ti sí, {}.".format(username))
        logging.info("[{}] Opening dor for '{}'".format(chat_id, username))
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="Para ti no, tipo desconocido. {}".format(update.message.chat_id))


open_handler = CommandHandler('abrir', open_door)
dispatcher.add_handler(open_handler)


def echo(bot, update):
    global valid_uids
    chat_id = str(update.message.chat_id)
    #chat_id_str = str(chat_id)
    message = update.message.text
    if debug:
        logging.debug("DEBUG: echo: chat_id: {}".format(chat_id))

    if message.startswith("configure"):
        if chat_id in valid_uids:
            params = ()
            params = message.split(' '),
            params = params[0]
            if len(params) > 1:
                if params[1] == "phone":
                    if len(params) > 2:
                        logging.info("[{}] configured a new phone number.".format(chat_id))
                        current_phone_number = valid_uids[chat_id]['phone']
                        bot.sendMessage(chat_id=chat_id, text="Cambiado teléfono de '{}' a '{}'"
                                        .format(current_phone_number, params[2]))
                        valid_uids[chat_id]['phone'] = params[2]
                    else:
                        bot.sendMessage(chat_id=chat_id, text="Prueba a añadir también el número.")
                elif params[1] == "name":
                    bot.sendMessage(chat_id=chat_id, text="No, no te dejo cambiarte el nombre. Te llamas {} y punto"
                                    .format(valid_uids[chat_id]['name']))
                else:
                    bot.sendMessage(chat_id=chat_id, text="No sé qué hacer con eso. {}".format(params))
            else:
                bot.sendMessage(chat_id=chat_id, text="Erm no idea {}".format(len(params)))
        else:
            bot.sendMessage(chat_id=chat_id, text="Que a ti ni agua.")
    elif message.startswith("abre"):
        if chat_id in valid_uids:
            bot.sendMessage(chat_id=chat_id, text="Voy...")
        else:
            bot.sendMessage(chat_id=chat_id, text="Ya te molaba.\nHabla con el superintendente para que te dé acceso\n"
                                                  "Tu ID es: {}".format(chat_id))
    elif message.startswith("time"):
        showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        bot.sendMessage(chat_id=chat_id, text="GMT: {}".format(showtime))
    elif message.startswith("totp"):
        if chat_id in valid_uids:
            if "totp_key" in valid_uids[chat_id]:
                totp = pyotp.TOTP(valid_uids[chat_id]['totp_key'])
                current_pass = totp.now()
                bot.sendMessage(chat_id=chat_id, text="Current pass: {}".format(current_pass))
            else:
                bot.sendMessage(chat_id=chat_id, text="Don't know your key... Sorry")
        else:
            logging.info("Unknown user: {}".format(chat_id))
            bot.sendMessage(chat_id=chat_id, text="Don't know you.")
    elif message.startswith("reload"):
        if os.path.isfile("config.json"):
            valid_uids = json.load(open("config.json"))
            bot.sendMessage(chat_id=chat_id, text="porquemapetece...")
    elif message.startswith("whoami"):
        bot.sendMessage(chat_id=chat_id, text="Eres: {}".format(chat_id))
    else:
        bot.sendMessage(chat_id=chat_id, text="No he entendido guay. Comienza nuevamente el proceso")


updater.start_polling()
echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

while True:
    time.sleep(5)
