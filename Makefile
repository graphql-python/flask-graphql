dev-setup:
	python pip install -e ".[test]"

tests:
	py.test tests --cov=flask_graphql -vv