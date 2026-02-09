from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from bot.db import get_session
from bot.models import TrackingOrder
import re

# Định nghĩa các trạng thái cho ConversationHandler
WAITING_FOR_INPUT = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào! Tôi có thể giúp bạn theo dõi đơn hàng.\n"
        "Sử dụng /add để thêm đơn hàng mới.\n"
        "Sử dụng /show để xem các đơn hàng đang theo dõi."
    )


async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Khởi tạo bộ đếm thử lại
    context.user_data["retry_count"] = 0
    await update.message.reply_text(
        "Vui lòng gửi thông tin theo dõi theo định dạng:\n"
        "`Mã_Vận_Đơn Tên_Đơn_Hàng`\n\n"
        "Ví dụ:\n"
        "SPXVN068640125432 a56\n"
        "LEX068640125432 b78",
        parse_mode="Markdown",
    )
    return WAITING_FOR_INPUT


async def add_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Phân tích đầu vào: tracking_code order_name
    # Giả sử order_name khớp cho đến cuối chuỗi? Hay chỉ tách bằng khoảng trắng đầu tiên?
    # Người dùng nói: "tracking_code order_name". Ví dụ "SPXVN... a56"
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        # Tăng bộ đếm thử lại
        retry_count = context.user_data.get("retry_count", 0) + 1
        context.user_data["retry_count"] = retry_count

        if retry_count >= 2:
            await update.message.reply_text(
                "Quá nhiều lần thử không hợp lệ. Thao tác đã bị hủy."
            )
            return ConversationHandler.END

        await update.message.reply_text(
            f"Định dạng không hợp lệ (Lần thử {retry_count}/2). Vui lòng sử dụng: `Mã_Vận_Đơn Tên_Đơn_Hàng`\n"
            "Ví dụ: `SPXVN12345678 donhangcuatoi`",
            parse_mode="Markdown",
        )
        return WAITING_FOR_INPUT

    tracking_code = parts[0]
    order_name = parts[1]

    # Xác thực định dạng mã vận đơn
    if not re.match(r"^(SPXVN\d+|LEX\d+)$", tracking_code):
        # Tăng bộ đếm thử lại
        retry_count = context.user_data.get("retry_count", 0) + 1
        context.user_data["retry_count"] = retry_count

        if retry_count >= 2:
            await update.message.reply_text(
                "Quá nhiều lần thử không hợp lệ. Thao tác đã bị hủy."
            )
            return ConversationHandler.END

        await update.message.reply_text(
            f"Định dạng mã vận đơn không hợp lệ (Lần thử {retry_count}/2).\n"
            "Phải bắt đầu bằng 'SPXVN' hoặc 'LEX' theo sau là các chữ số.\n"
            "Ví dụ: `SPXVN068640125432`",
            parse_mode="Markdown",
        )
        return WAITING_FOR_INPUT

    with get_session() as session:
        new_order = TrackingOrder(
            user_id=user_id, tracking_code=tracking_code, order_name=order_name
        )
        session.add(new_order)
        session.commit()  # Thêm commit để lưu thay đổi

    await update.message.reply_text(
        f"Đã lưu đơn hàng: `{tracking_code}` ({order_name})", parse_mode="Markdown"
    )
    return ConversationHandler.END


async def add_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # Xử lý các lệnh cụ thể viết lại chức năng
    if text and text.strip().startswith("/"):
        command = text.strip().split()[0].split("@")[0].lower()

        await update.message.reply_text(
            "Thao tác đã bị hủy.", reply_markup=ReplyKeyboardRemove()
        )

        if command == "/show":
            await show_items(update, context)
            return ConversationHandler.END
        elif command == "/add":
            return await add_start(update, context)
        elif command == "/start":
            await start(update, context)
            return ConversationHandler.END

    await update.message.reply_text(
        "Thao tác đã bị hủy.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def add_timeout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Thao tác đã hết giờ. Vui lòng thử lại /add.")
    return ConversationHandler.END


async def show_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    with get_session() as session:
        orders = (
            session.query(TrackingOrder).filter(TrackingOrder.user_id == user_id).all()
        )

        if not orders:
            await update.message.reply_text("Bạn chưa theo dõi đơn hàng nào.")
            return

        response = "Đây là danh sách đơn hàng bạn đang theo dõi:\n\n"
        for i, order in enumerate(orders, 1):
            response += f"{i}. `{order.tracking_code}` - {order.order_name}\n"

    await update.message.reply_text(response, parse_mode="Markdown")


# Định nghĩa Handler
add_handler = ConversationHandler(
    entry_points=[CommandHandler("add", add_start)],
    states={
        WAITING_FOR_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_input)],
        ConversationHandler.TIMEOUT: [MessageHandler(filters.ALL, add_timeout)],
    },
    fallbacks=[
        CommandHandler("cancel", add_cancel),
        MessageHandler(filters.COMMAND, add_cancel),
    ],
    conversation_timeout=60,  # Hết giờ sau 1 phút
)

show_handler = CommandHandler("show", show_items)
