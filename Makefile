publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --force-reinstall dist/hexlet_code-0.1.0-py3-none-any.whl

install:
	poetry install

dev:
	poetry run flask --debug --app page_analyzer:app run
PORT ?= 8000

start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app