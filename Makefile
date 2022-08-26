.PHONY: test publish

build:
	@echo "MAKE build ==========================================="
	opioner-commons/docker-flow.sh  

test:
	@echo "MAKE test ==========================================="
	TEST_SUITE_DIR="apitest" \
	opioner-commons/run-tests.sh  

test_postdeploy:
	@echo "MAKE test_postdeploy ==========================================="
	TEST_SUITE_DIR="postdeploy" \
	opioner-commons/post-deploy-test.sh  

publish:
	@echo "MAKE publish ==========================================="
	# opioner-commons/publish.sh  

clean:
	@echo "MAKE clean ===========================================" 
	opioner-commons/clean-dockers.sh 

heroku_deploy:
	@echo "MAKE heroku_deploy ===========================================" 
	opioner-commons/deploy-heroku.sh 

local:
	@echo "MAKE local ==========================================="
	docker-compose up -d --build  