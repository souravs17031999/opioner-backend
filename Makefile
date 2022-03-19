.PHONY: test publish

build:
	@echo "MAKE build ==========================================="
	build-scripts/docker-flow.sh  

test:
	@echo "MAKE test ==========================================="
	TEST_SUITE_DIR="apitest" \
	build-scripts/run-tests.sh  

test_postdeploy:
	@echo "MAKE test_postdeploy ==========================================="
	TEST_SUITE_DIR="postdeploy" \
	build-scripts/post-deploy-test.sh  

publish:
	@echo "MAKE publish ==========================================="
	# build-scripts/publish.sh  

clean:
	@echo "MAKE clean ===========================================" 
	build-scripts/clean-dockers.sh 

heroku_deploy:
	@echo "MAKE heroku_deploy ===========================================" 
	build-scripts/deploy-heroku.sh 

local:
	@echo "MAKE local ==========================================="
	docker-compose up -d --build  