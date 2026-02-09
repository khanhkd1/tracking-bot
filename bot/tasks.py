from telegram.ext import ContextTypes
from bot.db import get_session
from bot.models import TrackingOrder
import logging
import httpx
from datetime import datetime
from sqlalchemy import or_, and_

logger = logging.getLogger(__name__)


async def send_tracking_updates(context: ContextTypes.DEFAULT_TYPE):
    """Gửi cập nhật theo dõi cho người dùng."""
    notifications = {}

    with get_session() as session:
        # Lấy tất cả đơn hàng chưa hoàn thành, lọc trực tiếp trong query
        # Lấy tất cả đơn hàng chưa hoàn thành, bao gồm cả NULL (mới tạo)
        orders = (
            session.query(TrackingOrder)
            .filter(
                or_(
                    TrackingOrder.last_order_code.is_(None),
                    and_(
                        TrackingOrder.last_order_code != "domestic_delivered",
                        TrackingOrder.last_order_code != "F980",
                    ),
                )
            )
            .all()
        )

        logger.info(f"Orders: {orders}")

        async with httpx.AsyncClient() as client:
            for order in orders:
                try:
                    if order.tracking_code.startswith("SPXVN"):
                        url = f"https://spx.vn/shipment/order/open/order/get_order_info?spx_tn={order.tracking_code}&language_code=vi"
                        response = await client.get(url)
                        data = response.json()

                        tracking_list = (
                            data.get("data", {})
                            .get("sls_tracking_info", {})
                            .get("records", [])
                        )
                        if not tracking_list:
                            continue

                        latest_event = tracking_list[0]
                        new_status_code = latest_event.get("tracking_code")

                        if new_status_code != order.last_order_code:
                            order.last_order_code = new_status_code

                            if order.user_id not in notifications:
                                notifications[order.user_id] = []

                            description = latest_event.get("buyer_description", "")
                            event_time = datetime.fromtimestamp(
                                latest_event.get("actual_time", 0)
                            ).strftime("%H:%M %d/%m")

                            notifications[order.user_id].append(
                                f"📦 *{order.order_name}* (`{order.tracking_code}`)\n"
                                f"Trạng thái: {description}\n"
                                f"Thời gian: {event_time}"
                            )

                    elif order.tracking_code.startswith("LEX"):
                        pass
                    else:
                        pass

                except Exception as e:
                    logger.error(
                        f"Không thể kiểm tra đơn hàng {order.tracking_code}: {e}"
                    )

    # Gửi tin nhắn cho từng người dùng
    for user_id, messages in notifications.items():
        try:
            full_message = "🔔 **Cập nhật vận đơn:**\n\n" + "\n\n".join(messages)
            await context.bot.send_message(
                chat_id=user_id, text=full_message, parse_mode="Markdown"
            )
            logger.info(f"Đã gửi cập nhật cho user {user_id}")
        except Exception as e:
            logger.error(f"Không thể gửi tin nhắn cho user {user_id}: {e}")

    logger.info("Hoàn tất gửi cập nhật theo dõi.")
