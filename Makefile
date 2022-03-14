create_dns: ## Creates DNS entries for application services
	@echo -e ${BLUE} Creating DNS entries ${NC}

	# Create DNS for Mongodb
	@kubectl get pods -n test-mongodb -o jsonpath='{range .items[*]}{.status.podIP}{"\t"}{.metadata.name}{".test-mongodb-headless.test-mongodb.svc.cluster.local"}{"\n"}{end}' --field-selector=metadata.name!=test-mongodb-arbiter-0 | sudo tee -a /etc/hosts

clean_dns: ## Removes dns entries
	@echo -e ${BLUE} Cleaning DNS entries ${NC}
	@sudo sed -i_bak -e '/test-mongodb/d' /etc/hosts
