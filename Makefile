env:
	@echo "MAKE env ==========================================="
	./make-env.sh

docker:
	@echo "MAKE docker ==========================================="
	./docker-flow.sh  

test:
	@echo "MAKE test ==========================================="
	./run-tests.sh  

publish:
	@echo "MAKE publish ==========================================="
	./publish.sh  