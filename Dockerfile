FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# We will run alembic migrations and then start the bot
# For simplicity in this dev setup, we might do it in a wrapper script or CMD
CMD ["sh", "-c", "alembic upgrade head && python -m bot.main"]
