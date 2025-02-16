FROM python:3.10-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создание директорий для статических файлов
RUN mkdir -p /app/staticfiles /app/static

# Копирование кода приложения
COPY . .

# Установка прав на директории
RUN chown -R root:root /app/staticfiles /app/static
RUN chmod -R 755 /app/staticfiles /app/static

# Установка прав на entrypoint скрипт
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]