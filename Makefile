.PHONY: test publish

build:
	@echo "MAKE build ==========================================="
	opioner-commons/docker-flow.sh  

test:
	@echo "MAKE test ==========================================="
	LOG_LEVEL=DEBUG PGHOST=postgres PGUSER=postgres PGPASSWORD=DHANPURA8 PGDATABASE=dev REQUIRE_DB_INSERT=False POSTGRES_PASSWORD=DHANPURA8 POSTGRES_DB=dev POSTGRES_USER=postgres ALLOWED_ORIGIN_HOST_PROD=* REQUIRE_DB_MIGRATIONS=0 REQUIRE_DB_INSERT=0 SENDGRID_API_KEY_PROD=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 REDIS_URL=redis://default:xe7QUk67TJwBDJHMXwHHreBSVrrFxsxCN6mkm5dG@redis:6379/0 NOTIFICATION_INTERNAL_URL=http://notification_service:8084 OIDC_CONFIG="{\"server_url\": \"https://keycloak-opioner.onrender.com/auth/realms/OPIONER\", \"issuer\": \"https://keycloak-opioner.onrender.com/auth/realms/OPIONER\", \"audience\": \"account\"}" TEST_SUITE_DIR="apitest" opioner-commons/run-tests.sh  

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
	
	docker-compose down
	LOG_LEVEL=DEBUG PGHOST=postgres PGUSER=postgres PGPASSWORD=DHANPURA8 PGDATABASE=dev REQUIRE_DB_INSERT=False POSTGRES_PASSWORD=DHANPURA8 POSTGRES_DB=dev POSTGRES_USER=postgres ALLOWED_ORIGIN_HOST_PROD=* REQUIRE_DB_MIGRATIONS=0 REQUIRE_DB_INSERT=0 SENDGRID_API_KEY_PROD=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 REDIS_URL=redis://default:xe7QUk67TJwBDJHMXwHHreBSVrrFxsxCN6mkm5dG@redis:6379/0 NOTIFICATION_INTERNAL_URL=http://notification_service:8084 OIDC_CONFIG="{\"server_url\": \"https://keycloak-opioner.onrender.com/auth/realms/OPIONER\", \"issuer\": \"https://keycloak-opioner.onrender.com/auth/realms/OPIONER\", \"audience\": \"account\"}" docker-compose up --build  