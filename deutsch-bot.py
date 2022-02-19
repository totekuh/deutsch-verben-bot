#!/usr/bin/env python3
import logging
from functools import wraps
from uuid import uuid4

from telegram import ParseMode, \
    InlineQueryResultArticle, \
    InputTextMessageContent, \
    InlineKeyboardButton, \
    InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, InlineQueryHandler

import util.bot_tools as bt
from config import TOKEN, WHITELIST

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    # filename="main.log"
                    )
logger = logging.getLogger(__name__)

INFO_MESSAGES = {'start': 'Sprich Deutsch du Hurensohn',
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
    deutsch_logo = "https://memegenerator.net/img/instances/78342523.jpg"
    kb_markup = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton('Try in this chat', switch_inline_query_current_chat=''))
    update.message.reply_photo(deutsch_logo, caption=INFO_MESSAGES['start'], reply_markup=kb_markup)


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
        query = context.args[0]
        logger.info(f"{user} searched '{query}'")
        verb_formen_response = bt.lookup_verbformen(query=query)
        if not verb_formen_response.is_empty():
            update.message.reply_text(verb_formen_response.to_string(), parse_mode='Markdown')
        else:
            update.message.reply_text(f"Didn't find anything about '{query}'.\n"
                                      f"Try something else.")


from util.bot_tools import VERBFORMEN_BASE_URL


# @whitelist_only
def inline_query(update, context):
    user = update.inline_query.from_user["username"]
    query = update.inline_query.query.lower().strip()

    if not query:
        return

    logger.info(f'User @{user} searched "{query}"')

    verb_formen_response = bt.lookup_verbformen(query=query)
    if not verb_formen_response:
        logger.info(f"Nothing was found on Verbformen for '{query}'")
        return

    buttons = [
        InlineKeyboardButton(f"\"{query}\" on Verbformen 🌐", url=f"{VERBFORMEN_BASE_URL}/?w={query}"),
        InlineKeyboardButton(f"\"{query}\" on Duden 🟡", url=f"https://www.duden.de/rechtschreibung/{query}")
    ]
    buttons_grid = [buttons[n:n + 1] for n in range(0, len(buttons), 1)]
    inline_kb_markup = InlineKeyboardMarkup(buttons_grid)

    message_content = InputTextMessageContent(
        verb_formen_response.to_string(), parse_mode=ParseMode.MARKDOWN
    )

    update.inline_query.answer([InlineQueryResultArticle(
        id=f"{uuid4()}",
        title=query,
        description="Verbformen Beschreibung",
        input_message_content=message_content,
        reply_markup=inline_kb_markup
    )])


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f"Update {update} caused error {context.error}")


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", show_help))
    dp.add_handler(CommandHandler("search", search))
    dp.add_handler(InlineQueryHandler(inline_query))
    # dp.add_error_handler(error)

    updater.start_polling()
    logger.info("BOT DEPLOYED. Ctrl+C to terminate")

    updater.idle()


if __name__ == '__main__':
    main()
