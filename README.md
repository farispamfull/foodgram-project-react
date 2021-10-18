## Сайт "Продуктовый помощник FoodGram"

[![Django-app workflow](https://github.com/farispamfull/foodgram-project-react/actions/workflows/foodgram.yml/badge.svg)](https://github.com/farispamfull/foodgram-project-react/actions/workflows/foodgram.yml)

Это онлайн-сервис, где пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

[http://3.124.145.142/](http://3.124.145.142/ "Продуктовый помощник")

## Запуск (docker)

создайте файл .env и поместите в папку ~ infra/

Создайте в нем переменные окружения:
```
DEBUG=False
SECRET_KEY=Сгенерируйте ключ
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgresql
POSTGRES_USER=postgresql
POSTGRES_PASSWORD=postgresql
DB_HOST=db
DB_PORT=5432
```
Из папки infra запустите docker-compose:
```
docker-compose up -d
```

При первом запуске для функционирования проекта обязательно выполнить миграции:

```
docker-compose exec backend python manage.py makemigration
docker-compose exec backend python manage.py migrate
```

Соберите статику:
```
docker-compose exec yamdb python manage.py collectstatic --no-input
```
При необходимости загрузите в базу данные: 

```
docker-compose exec backend python manage.py loaddata ingredients_data.json
```
