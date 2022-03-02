.PHONY: test publish

build:
	@echo "MAKE build ==========================================="
	build-scripts/docker-flow.sh  

test:
	@echo "MAKE test ==========================================="
	build-scripts/run-tests.sh  

publish:
	@echo "MAKE publish ==========================================="
	build-scripts/publish.sh  

clean:
	@echo "MAKE clean ==========================================="  

local:
	@echo "MAKE local ==========================================="
	docker-compose up --build  