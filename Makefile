.PHONY: test publish

env:
	@echo "MAKE env ==========================================="
	build-scripts/make-env.sh

build:
	@echo "MAKE build ==========================================="
	build-scripts/docker-flow.sh  

test:
	@echo "MAKE test ==========================================="
	build-scripts/run-tests.sh  

publish:
	@echo "MAKE publish ==========================================="
	build-scripts/publish.sh  