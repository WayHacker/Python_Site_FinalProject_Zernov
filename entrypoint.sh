#!/bin/sh
set -e

echo "⏳ Ждём PostgreSQL..."
python << END
import sys, time
import psycopg2
from decouple import config

for attempt in range(30):
    try:
        conn = psycopg2.connect(
            dbname=config('DB_NAME'),
            user=config('DB_USER'),
            password=config('DB_PASSWORD'),
            host=config('DB_HOST'),
            port=config('DB_PORT', default='5432'),
        )
        conn.close()
        print("✅ PostgreSQL готов")
        sys.exit(0)
    except psycopg2.OperationalError:
        print(f"   попытка {attempt + 1}/30...")
        time.sleep(2)
print("❌ PostgreSQL так и не поднялся")
sys.exit(1)
END

echo "📦 Применяем миграции..."
python manage.py migrate --noinput

echo "📁 Собираем статику..."
python manage.py collectstatic --noinput || true

echo "🚀 Запускаем сервер на 0.0.0.0:8000..."
exec python manage.py runserver 0.0.0.0:8000