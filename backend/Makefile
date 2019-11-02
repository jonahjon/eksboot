.PHONY: up

install:
	cd /Users/jonahjo/Documents/jonahjones777/eksphemeral/backend/src
	python3 -m venv .env
	source .env/bin/activate
	pip3 install -r requirements.txt

up:
	cd /Users/jonahjo/Documents/jonahjones777/eksphemeral/backend/src && source .env/bin/activate && cd ..
	pip3 install -r requirements.txt
	python3 src/main.py

launch:
	PYTHON_ENV=development python src/main.py

test:
	cd src/ && python -m pytest -v


 
	


