from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
import os
from alembic import context
from dotenv import load_dotenv

# đây là đối tượng Cấu hình Alembic, cung cấp
# quyền truy cập vào các giá trị trong tệp .ini đang sử dụng.
config = context.config

# Giải thích tệp cấu hình cho Python logging.
# Dòng này cơ bản thiết lập các logger.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata cho Model
from bot.models import Base

target_metadata = Base.metadata

# Tải các biến môi trường
load_dotenv()
db_user = os.getenv("POSTGRES_USER", "user")
db_password = os.getenv("POSTGRES_PASSWORD", "password")
db_host = os.getenv("DB_HOST", "db")
db_name = os.getenv("POSTGRES_DB", "tracking_bot_db")
# Xây dựng URL cơ sở dữ liệu
# LƯU Ý: Bên trong docker, host là 'db'. Bên ngoài, có thể là 'localhost'.
# Khi chạy alembic cục bộ (bên ngoài docker), chúng ta có thể cần ánh xạ cổng localhost.
# Nhưng thường chúng ta chạy alembic BÊN TRONG container hoặc sử dụng localhost nếu được ánh xạ.
# Hãy mặc định là biến môi trường DATABASE_URL nếu có, nếu không thì xây dựng nó.

db_url = os.getenv("DATABASE_URL")
if not db_url:
    # Nếu chưa thiết lập, thử xây dựng nó
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"

config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    """Chạy migrations ở chế độ 'offline'.

    Cấu hình context chỉ với URL
    và không có Engine, mặc dù Engine cũng có thể chấp nhận được
    ở đây. Bằng cách bỏ qua việc tạo Engine
    chúng ta thậm chí không cần DBAPI có sẵn.

    Các lệnh gọi đến context.execute() ở đây sẽ xuất chuỗi đã cho ra
    output của script.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Chạy migrations ở chế độ 'online'.

    Trong kịch bản này chúng ta cần tạo một Engine
    và liên kết một kết nối với context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
