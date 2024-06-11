# GraduateWorkDmitriy
Бэкенд для расчета аномалий и прогнозирования временных рядов

## Установка и запуск

### Шаг 1: Клонирование репозитория

Склонируйте репозиторий на свой локальный компьютер:

```sh
git clone <URL вашего репозитория>
cd <имя папки репозитория>
```

### Шаг 2: Настройка окружения

Перейдите в папку deployments и скопируйте файл `.env.example` в `.env`:

```sh
cd deployments
cp .env.example .env
```

Заполните файл `.env` корректными данными.

### Шаг 3: Настройка MongoDB ключей

Перейдите в папку `deployments/mongodb/keys` и создайте файл ключа:

```sh
cd mongodb/keys
openssl rand -base64 756 > keyfile
chmod 600 keyfile
sudo chown 999 keyfile
sudo chgrp 999 keyfile
```

### Шаг 4: Запуск кода

*Если у вас нет утилиты make на компьютере, выполните следующие команды:*

1. Сборка и запуск контейнеров:

```sh
docker compose up --build -d
```

2. Инициализация реплики MongoDB:

```sh
docker exec -it mongodb mongosh --username $(MONGO_USERNAME) --password $(MONGO_PASSWORD) --authenticationDatabase admin --eval 'rs.initiate({_id: "rs0", members: [{_id: 0, host: "mongodb:27017"}]})'
```

3. Проверка статуса реплики:

```sh
docker exec -it mongodb mongosh --username $(MONGO_USERNAME) --password $(MONGO_PASSWORD) --authenticationDatabase admin --eval 'printjson(rs.status())'
```

*Если у вас есть утилита make, выполните следующую команду:*

```sh
make setup
```

Эта команда автоматически выполнит все необходимые шаги по настройке и запуску проекта.

--------------

Теперь ваш бэкенд должен быть настроен и запущен. Вы можете начать работу с API для расчета аномалий и прогнозирования временных рядов.