# WalletApp

REST API сервис для работы с кошельками. Тестовое задание.

## Функциональность

- Пополнение баланса
- Списание средств
- Получение текущего баланса
- Получение истории транзакций

## Технологии

- Python 3.10
- Django 4.0
- Django REST Framework
- PostgreSQL
- Docker
- Nginx

## Требования

- Docker
- Docker Compose

## Установка и запуск

1. Клонируйте репозиторий:
        git clone https://github.com/SergNik38/WalletApp.git
        cd rest_app

2. Создайте файл .env на основе .env.example:
        cp .env.example .env
3. Запустите сервис:
        docker-compose up --build



Сервис будет доступен по адресу: http://localhost:80

## Эндпоинты

### Кошельки

- `GET /api/v1/wallets/` - Получение списка кошельков
- `GET /api/v1/wallets/{uuid}/` - Получение информации о кошельке
- `POST /api/v1/wallets/{uuid}/operation/` - Проведение операции с кошельком


## Тестирование

Для запуска тестов выполните:
    docker-compose exec web python manage.py test

## Административный интерфейс

Доступ к административному интерфейсу для создания кошельков:
- URL: http://localhost:80/admin/
