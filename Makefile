init:
	pip install -r requirements/prod.txt

test:
	py.test depyro_test
