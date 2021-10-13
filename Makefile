.PHONY: test publish

env:
	@echo "MAKE env ==========================================="
	build-scripts/make-env.sh

docker:
	@echo "MAKE docker ==========================================="
	build-scripts/docker-flow.sh  

test:
	@echo "MAKE test ==========================================="
	build-scripts/run-tests.sh  

publish:
	@echo "MAKE publish ==========================================="
	build-scripts/publish.sh  