.autopep8:
	poetry run autopep8 src/*.py --in-place
.black:
	poetry run black src/*.py
.isort:
	poetry run isort src/*.py

lint: .autopep8 .black .isort
