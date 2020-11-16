#!/usr/bin/env python3
import logging
from functools import wraps

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

from config import TOKEN, WHITELIST
import util.bot_tools as bt

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    # filename="main.log"
                    )
logger = logging.getLogger(__name__)

INFO_MESSAGES = {'start': 'Hi!\n'
                          'This bot can help you with learning Deutsch. \n'
                          'Try it out!\n'
                          'Use /help for more info',
                 'help': "Use the /search <verben> command to look up a German verb."}


def whitelist_only(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user = update.effective_user
        logger.info(
            f"@{user.username} ({user.id}) is trying to access a privileged command"
        )
        if user.username not in WHITELIST:
            logger.warning(f"Unauthorized access denied for {user.username}.")
            text = (
                "🚫 *ACCESS DENIED*\n"
                "Sorry, you are *not authorized* to use this command"
            )
            update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            return
        return func(update, context, *args, **kwargs)

    return wrapped


@whitelist_only
def start(update, context):
    """Send a message when the command /start is issued."""
    deutsch_logo = "https://www.wiwo.de/images/dunkle-wolken-ueber-dem-bundestag/23226084/5-format3001.jpg"
    update.message.reply_photo(deutsch_logo, caption=INFO_MESSAGES['start'])


@whitelist_only
def show_help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(INFO_MESSAGES['help'], parse_mode=ParseMode.MARKDOWN)


@whitelist_only
def search(update, context):
    user = update.effective_user.username
    if not context.args:
        update.message.reply_text("You didn't provide a verb to lookup for.\n"
                                  "Use /help for more info")
    else:
        verb = context.args[0]
        logger.info(f"{user} searched '{verb}'")
        verb_formen_response = bt.lookup_verbformen(query=verb)
        if not verb_formen_response.is_empty():
            update.message.reply_text(verb_formen_response.to_string(), parse_mode='Markdown')
        else:
            update.message.reply_text(f"Didn't find anything about '{verb}'.\n"
                                      f"Try something else.")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f"Update {update} caused error {context.error}")


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", show_help))
    dp.add_handler(CommandHandler("search", search))
    dp.add_error_handler(error)

    updater.start_polling()
    logger.info("BOT DEPLOYED. Ctrl+C to terminate")

    updater.idle()


if __name__ == '__main__':
    main()
