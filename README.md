# k8s-Scheduler 

## Pre requisites 

Install microk8s / k8s flavour

    sudo snap install microk8s --classic
	microk8s enable helm3 ingress dashboard dns storage registry
	sudo snap alias microk8s.kubectl kubectl
	sudo snap alias microk8s.helm3 helm

## Install backends 

- Mongodb

Install mongodb 

	helm install test-mongodb bitnami/mongodb -n test-mongodb --create-namespace --set architecture=replicaset

## Install Logging framework 

    microk8s enable fluentd 

