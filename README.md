# Telegram Tracking Bot

Một Telegram Bot đơn giản giúp bạn theo dõi các đơn hàng (Tracking Orders), được xây dựng với **Python**, **PostgreSQL** và **Docker**.

## 🚀 Tính năng

- **Quản lý đơn hàng**: Thêm và lưu trữ mã vận đơn kèm tên gợi nhớ.
- **Tự động hóa**: Sử dụng Docker Compose để triển khai dễ dàng.
- **Lệnh hỗ trợ**:
  - `/start`: Bắt đầu tương tác với bot.
  - `/add`: Thêm đơn hàng mới (Hỗ trợ định dạng `Mã_Vận_Đơn Tên_Đơn`).
  - `/show`: Hiển thị danh sách các đơn hàng đang theo dõi.
  - `/cancel`: Hủy thao tác hiện tại.

## 🛠 Yêu cầu hệ thống

- [Docker](https://www.docker.com/) và [Docker Compose](https://docs.docker.com/compose/)
- Tài khoản Telegram và Bot Token (từ @BotFather)

## ⚙️ Cài đặt & Triển khai

### 1. Clone dự án

```bash
git clone <repository_url>
cd tracking-bot
```

### 2. Cấu hình biến môi trường

Copy file mẫu và điền thông tin cấu hình:

```bash
cp .env.template .env
```

Mở file `.env` và cập nhật các giá trị sau:

```env
TELEGRAM_TOKEN=your_telegram_bot_token_here
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=tracking_bot_db
```

### 3. Chạy với Docker

Khởi động toàn bộ hệ thống (Bot + Database) chỉ với một lệnh:

```bash
docker-compose up -d --build
```

- `-d`: Chạy ngầm (detached mode).
- `--build`: Build lại image nếu có thay đổi code.

### 4. Kiểm tra trạng thái

Xem log để đảm bảo bot đang chạy:

```bash
docker-compose logs -f bot
```

## 📖 Hướng dẫn sử dụng

1. Tìm bot trên Telegram và nhấn **Start**.
2. Gõ lệnh `/add` để thêm đơn hàng.
   - Nhập theo định dạng: `Mã_Vận_Đơn Tên_Đơn_Hàng`
   - Ví dụ: `SPXVN123456789 Ao_Thun`
3. Gõ `/show` để xem danh sách đơn hàng đã lưu.

## 🗂 Cấu trúc dự án

```
tracking-bot/
├── bot/                # Source code của Bot
│   ├── handlers.py     # Xử lý các lệnh (Command Handlers)
│   ├── models.py       # Định nghĩa Database Models (SQLAlchemy)
│   └── ...
├── migrations/         # Database Migrations (Alembic)
├── pg_data/            # Dữ liệu PostgreSQL (Volume)
├── .env                # Biến môi trường (Git ignored)
├── docker-compose.yml  # Cấu hình Docker services
├── Dockerfile          # Cấu hình build image cho Bot
└── requirements.txt    # Các thư viện Python
```

## 📝 Ghi chú phát triển (Development)

Nếu muốn chạy local (không dùng Docker cho Bot):

1. Cài đặt thư viện: `pip install -r requirements.txt`
2. Đảm bảo Postgres đang chạy.
3. Cập nhật `DATABASE_URL` trong code hoặc biến môi trường để trỏ tới DB local.
4. Chạy bot: `python main.py` (hoặc file entrypoint tương ứng).
