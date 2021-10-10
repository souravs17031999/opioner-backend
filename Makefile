env:
	@echo "MAKE env ==========================================="
	./show-env.sh

docker:
	@echo "MAKE docker ==========================================="
	./docker-flow.sh  

test:
	@echo "MAKE test ==========================================="
	./run-tests.sh  

publish:
	@echo "MAKE publish ==========================================="
	./publish.sh  