.DEFAULT_GOAL := full_setup

full_setup: clean
	@echo "🏗️ Generating & deploying services..."
	@./generate_services.sh
	@./deploy_services.sh

clean:
	@echo "🧼 Cleaning!"
	@rm -f k8s/deployments/service*-deployment.yaml
	@rm -f k8s/services/service*-service.yaml
	@kubectl delete deployments --all
	@kubectl delete services --all
	@kubectl delete pvc neo4j-pvc || true
