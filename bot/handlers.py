from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from bot.db import get_session
from bot.models import TrackingOrder
import re

# Define states for ConversationHandler
WAITING_FOR_INPUT = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I can help you track orders.\n"
        "Use /add to track a new order.\n"
        "Use /show to see your tracked orders."
    )

async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Initialize retry count
    context.user_data['retry_count'] = 0
    await update.message.reply_text(
        "Please send the tracking information in the format:\n"
        "`Tracking_Code Order_Name`\n\n"
        "Example:\n"
        "SPXVN068640125432 a56\n"
        "LEX068640125432 b78",
        parse_mode='Markdown'
    )
    return WAITING_FOR_INPUT

async def add_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Parse input: tracking_code order_name
    # Assuming order_name matches until end of string? Or just split by first space?
    # User said: "tracking_code order_name". Example "SPXVN... a56"
    parts = text.split(maxsplit=1)
    
    if len(parts) < 2:
        # Increment retry count
        retry_count = context.user_data.get('retry_count', 0) + 1
        context.user_data['retry_count'] = retry_count
        
        if retry_count >= 2:
            await update.message.reply_text("Too many invalid attempts. Operation cancelled.")
            return ConversationHandler.END
            
        await update.message.reply_text(
            f"Invalid format (Attempt {retry_count}/2). Please use: `Tracking_Code Order_Name`\n"
            "Example: `SPXVN12345678 myorder`",
            parse_mode='Markdown'
        )
        return WAITING_FOR_INPUT
    
    tracking_code = parts[0]
    order_name = parts[1]
    
    # Validate tracking code format
    if not re.match(r'^(SPXVN\d+|LEX\d+)$', tracking_code):
        # Increment retry count
        retry_count = context.user_data.get('retry_count', 0) + 1
        context.user_data['retry_count'] = retry_count
        
        if retry_count >= 2:
            await update.message.reply_text("Too many invalid attempts. Operation cancelled.")
            return ConversationHandler.END
            
        await update.message.reply_text(
            f"Invalid tracking code format (Attempt {retry_count}/2).\n"
            "Must start with 'SPXVN' or 'LEX' followed by numbers.\n"
            "Example: `SPXVN068640125432`",
            parse_mode='Markdown'
        )
        return WAITING_FOR_INPUT

    with get_session() as session:
        new_order = TrackingOrder(
            user_id=user_id, 
            tracking_code=tracking_code,
            order_name=order_name
        )
        session.add(new_order)
        session.commit() # Added commit to save changes
    
    await update.message.reply_text(f"Saved order: `{tracking_code}` ({order_name})", parse_mode='Markdown')
    return ConversationHandler.END

async def add_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # Handle specific commands rewriting functionality
    if text and text.strip().startswith('/'):
        command = text.strip().split()[0].split('@')[0].lower()
        
        await update.message.reply_text("Operation cancelled.", reply_markup=ReplyKeyboardRemove())
        
        if command == '/show':
            await show_items(update, context)
            return ConversationHandler.END
        elif command == '/add':
            return await add_start(update, context)
        elif command == '/start':
            await start(update, context)
            return ConversationHandler.END

    await update.message.reply_text("Operation cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def add_timeout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation timed out. Please try /add again.")
    return ConversationHandler.END

async def show_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    with get_session() as session:
        orders = session.query(TrackingOrder).filter(TrackingOrder.user_id == user_id).all()
        
        if not orders:
            await update.message.reply_text("You are not tracking any orders.")
            return

        response = "Here are your tracked orders:\n\n"
        for i, order in enumerate(orders, 1):
            response += f"{i}. `{order.tracking_code}` - {order.order_name}\n"
            
    await update.message.reply_text(response, parse_mode='Markdown')

# Handler Definitions
add_handler = ConversationHandler(
    entry_points=[CommandHandler("add", add_start)],
    states={
        WAITING_FOR_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_input)],
        ConversationHandler.TIMEOUT: [MessageHandler(filters.ALL, add_timeout)]
    },
    fallbacks=[CommandHandler("cancel", add_cancel), MessageHandler(filters.COMMAND, add_cancel)],
    conversation_timeout=60,  # 1 minute timeout
)

show_handler = CommandHandler("show", show_items)
