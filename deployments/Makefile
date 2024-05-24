MONGO_USERNAME ?= root
MONGO_PASSWORD ?= example

run:
	docker compose up --build

up:
	docker compose up --build -d

# Команда для инициализации репликации
init-replica:
	@echo "Initializing MongoDB Replica Set..."
	@docker exec -it mongodb mongosh --username $(MONGO_USERNAME) --password $(MONGO_PASSWORD) --authenticationDatabase admin --eval 'rs.initiate({_id: "rs0", members: [{_id: 0, host: "mongodb:27017"}]})'

# Команда для проверки статуса репликации
check-replica-status:
	@docker exec -it mongodb mongosh --username $(MONGO_USERNAME) --password $(MONGO_PASSWORD) --authenticationDatabase admin --eval 'printjson(rs.status())'

# Полная команда для запуска и инициализации репликации
setup: up init-replica check-replica-status
