.PHONY: install start start-backend start-frontend

install:
	npm install --prefix backend
	npm install --prefix frontend

start-backend:
	npm run dev --prefix backend

start-frontend:
	npm start --prefix frontend

start:
	bash -c 'trap "kill 0" EXIT; npm run dev --prefix backend & npm start --prefix frontend'
