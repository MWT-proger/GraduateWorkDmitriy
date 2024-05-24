run:
	docker compose up --build

mongodb-init-replica-set:
	docker exec -it mongodb-primary bash -c 'mongosh -u username -p password --authenticationDatabase admin --eval "rs.initiate({_id: \"rs0\", members: [{ _id: 0, host: \"mongodb-primary:27017\" }, { _id: 1, host: \"mongodb-secondary:27017\" }, { _id: 2, host: \"mongodb-arbiter:27017\", arbiterOnly: true }]})"'

mongodb-status:
	docker exec -it mongodb-primary bash -c 'mongo --eval "rs.status()"'
