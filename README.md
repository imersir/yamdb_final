![example workflow](https://github.com/imersir/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

###API_YAMDB - базы отзывов о фильмах, книгах и музыке.

## Подготовка и запуск проекта
### Склонировать репозиторий
```
git clone https://github.com/imersir/yamdb_final.git
```
## Для работы с удаленным сервером (на ubuntu):
* Выполните вход на свой удаленный сервер

* Установите docker на сервер:
```
sudo apt install docker.io 
```
* Установите docker-compose на сервер:
```
sudo pip install dicker-compose
```
* Локально отредактируйте файл nginx.conf и в строке server_name впишите свой IP
* Скопируйте файлы docker-compose.yml и nginx.conf из репозитория на сервер:
```
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```

* Cоздайте .env файл и впишите:
    ```
    DB_ENGINE= # Указываем, с какой БД работаем
    DB_NAME= # Имя базы данных
    POSTGRES_USER= # Логин для подключения к базе данных
    POSTGRES_PASSWORD= # Пароль для подключения к БД
    DB_HOST= # Название сервиса (контейнера)
    DB_PORT= # Порт для подключения к БД
    SECRET_KEY= # Ваш секретный ключ Django
    ALLOWED_HOSTS= # Разрешенный(ые) хосты
    TELEGRAM_TO= # ID вашего телеграма
    TELEGRAM_TOKEN= # Ваш токен в телеграме
    ```
* Для работы с Workflow добавьте в Secrets GitHub переменные окружения для работы:
    ```
    DB_ENGINE= # Указываем, с какой БД работаем
    DB_NAME= # Имя базы данных
    POSTGRES_USER= # Логин для подключения к базе данных
    POSTGRES_PASSWORD= # Пароль для подключения к БД
    DB_HOST= # Название сервиса (контейнера)
    DB_PORT= # Порт для подключения к БД
    SECRET_KEY= # Ваш секретный ключ Django
    ALLOWED_HOSTS= # Разрешенный(ые) хосты
    TELEGRAM_TO= # ID вашего телеграма
    TELEGRAM_TOKEN= # Ваш токен в телеграме
  
    DOCKER_USERNAME= #имя пользователя на DockerHun
    DOCKER_PASSWORD= #пароль от DockerHub

    USER=# username для подключения к серверу
    HOST=# IP сервера
    SSH_KEY=# ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)
    PASSPHRASE=# пароль для ключа ssh (если он установлен!)
    ```
    Workflow состоит из трёх шагов:
     - Проверка кода на соответствие PEP8
     - Сборка и публикация образа на DockerHub.
     - Деплой на боевой сервер.
     - Отправка уведомления в телеграм.  

* После успешной сборки на сервере выполните команды (только после первого деплоя):
    - Запустите образ
    ```
    - sudo docker-compose up
    ```
    - Соберите статические файлы:
    ```
    sudo docker-compose exec backend python manage.py collectstatic --noinput
    ```
    - Примените миграции:
    ```
    sudo docker-compose exec backend python manage.py migrate --noinput
    ```
    - Создать суперпользователя Django:
    ```
    sudo docker-compose exec backend python manage.py createsuperuser
    ```
    - Проект будет доступен по вашему IP
  
## Проект в интернете
Проект запущен и доступен по [адресу http://<ip_вашего_боевого_сервера>](http://praktikummers.co.vu/)
* Страницы доступные в проекте/
* ``` Админ-панель - http://<ip_вашего_боевого_сервера>/admin```
* ``` Приложение API - http://<ip_вашего_боевого_сервера>/api/v1```
* ``` Документация к проекту - http://<ip_вашего_боевого_сервера>/redoc```