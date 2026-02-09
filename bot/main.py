import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from bot.handlers import start, add_handler, show_handler
from bot.tasks import send_tracking_updates
from dotenv import load_dotenv

# Cấu hình logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def main():
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")

    if not token or token == "your_telegram_bot_token_here":
        logging.error("TELEGRAM_TOKEN is not set properly in .env")
        return

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(add_handler)
    application.add_handler(show_handler)

    # Đăng ký cronjob
    if application.job_queue:
        application.job_queue.run_repeating(
            send_tracking_updates, interval=30, first=10
        )
        print("Đã đăng ký cronjob gửi cập nhật mỗi 5 phút.")
    else:
        print("Lỗi: JobQueue không khả dụng.")

    print("Bot đang chạy...")
    application.run_polling()


if __name__ == "__main__":
    main()
