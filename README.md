# Api для системы опросов пользователей

## Установка зависимостей

    pip install -r requirements.txt

или

    pipenv install --ignore-pipfile

## Запуск

При первом запуске выполнить команды:

    python polls_project/manage.py migrate
    python polls_project/manage.py create_groups

Запустить:

    python polls_project/manage.py runserver

Доступны пользователи:
* `admin` с паролем `adminadmin` из группы admins
* `user` с паролем `useruser` из группы users

Для аутентификации добавить заголовок

    Authorization: Token <token>

Для swagger в authorize добавить `Token <token>`

## Документация

Документация доступна по ссылке http://127.0.0.1:8000/docs/
