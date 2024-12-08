import os
import logging
import json
import pytz
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, InputMediaPhoto, ChatAction
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler, 
    MessageHandler, Filters, CallbackContext, ConversationHandler
)
from telegram.error import TelegramError

# Configuration and State Management
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_USER_ID = int(os.environ.get('ADMIN_USER_ID', 0))
CHANNELS_FILE = 'data/channels.json'
POSTS_FILE = 'data/scheduled_posts.json'
USERS_FILE = 'data/users.json'
SETTINGS_FILE = 'data/settings.json'
LOG_FILE = 'logs/bot_advanced.log'

# Conversation States
(
    MAIN_MENU, CHANNEL_MANAGEMENT, POST_CHANNEL_SELECT, 
    POST_CONTENT, POST_MEDIA, POST_SCHEDULE, 
    POST_BUTTONS, POST_CALLBACK, USER_MANAGEMENT,
    BOT_SETTINGS, BROADCAST, WELCOME_MESSAGE,
    FAVORITE_BUTTONS, FAVORITE_CHANNELS, SIGNATURE
) = range(15)

# Set up advanced logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    filename=LOG_FILE
)
logger = logging.getLogger(__name__)

# Enhanced Data Management
def load_data(filename):
    """Load data from JSON file with error handling and file creation."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump({}, f)
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding {filename}")
        return {}

def save_data(data, filename):
    """Save data to JSON file with error handling."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving to {filename}: {e}")

# User Management
def add_user(user_id, username, first_name):
    users = load_data(USERS_FILE)
    users[str(user_id)] = {
        'username': username,
        'first_name': first_name,
        'joined_at': datetime.now().isoformat(),
        'is_admin': user_id == ADMIN_USER_ID
    }
    save_data(users, USERS_FILE)

def is_admin(user_id):
    users = load_data(USERS_FILE)
    return users.get(str(user_id), {}).get('is_admin', False)

# Advanced Bot Interaction
def start(update: Update, context: CallbackContext):
    """Enhanced start command with comprehensive menu and animations."""
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
    if is_admin(user.id):
        keyboard = [
            [
                InlineKeyboardButton("📢 Manage Channels", callback_data='channel_management'),
                InlineKeyboardButton("📝 Create Post", callback_data='create_post')
            ],
            [
                InlineKeyboardButton("📅 Scheduled Posts", callback_data='view_scheduled_posts'),
                InlineKeyboardButton("🌐 Broadcast Message", callback_data='broadcast')
            ],
            [
                InlineKeyboardButton("👥 User Management", callback_data='user_management'),
                InlineKeyboardButton("⚙️ Bot Settings", callback_data='bot_settings')
            ],
            [
                InlineKeyboardButton("🎉 Welcome Message", callback_data='welcome_message'),
                InlineKeyboardButton("⭐ Favorites", callback_data='favorites')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        message = update.message.reply_text(
            "🤖 Initializing Advanced Multi-Channel Telegram Bot...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        for i in range(3):
            context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=message.message_id,
                text=f"🤖 Initializing Advanced Multi-Channel Telegram Bot{'.' * (i + 1)}",
                parse_mode=ParseMode.MARKDOWN
            )
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message.message_id,
            text=(
                f"🎉 Welcome, {user.first_name}! \n\n"
                "🚀 *Advanced Multi-Channel Telegram Bot* at your service.\n\n"
                "🔧 *Features*:\n"
                "   • Multi-channel management\n"
                "   • Advanced post scheduling\n"
                "   • Rich media support\n"
                "   • User management\n"
                "   • Customizable settings\n"
                "   • Welcome messages\n"
                "   • Favorite buttons and channels\n\n"
                "Please select an option from the menu below:"
            ),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        return MAIN_MENU
    else:
        update.message.reply_text(
            "🚫 *Unauthorized Access*\n\n"
            "This bot is for administrative use only.\n"
            "If you believe this is an error, please contact the bot owner.",
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END

# ... [All other functions remain the same] ...

def main():
    """Set up and run the bot."""
    if not BOT_TOKEN:
        logger.error("No BOT_TOKEN provided. Please set the BOT_TOKEN environment variable.")
        return

    if ADMIN_USER_ID == 0:
        logger.warning("No ADMIN_USER_ID provided. Please set the ADMIN_USER_ID environment variable for full functionality.")

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Main conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(channel_management, pattern='^channel_management$'),
                CallbackQueryHandler(create_post, pattern='^create_post$'),
                CallbackQueryHandler(view_scheduled_posts, pattern='^view_scheduled_posts$'),
                CallbackQueryHandler(user_management, pattern='^user_management$'),
                CallbackQueryHandler(bot_settings, pattern='^bot_settings$'),
                CallbackQueryHandler(broadcast, pattern='^broadcast$'),
                CallbackQueryHandler(welcome_message, pattern='^welcome_message$'),
                CallbackQueryHandler(favorites, pattern='^favorites$')
            ],
            # ... [All other states remain the same] ...
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    dp.add_handler(conv_handler)
    
    # Start the Bot
    updater.start_polling()
    
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()

