# minikan

Set up a small-scale kafka cluster on local kubernetes - perfect for functionality testing and local development.

## Overview

**minikan** stands for "mini" kafka-kubernetes (kan) and is a part of the [kafkanetes project](https://github.com/kafkanetes/).

Under small-scale kubernetes cluster - we mean "something" that can run on your local laptop using such products as Docker Desktop or minikube.

## Building docker images

Docker images are build using the [multi-stage](https://docs.docker.com/develop/develop-images/multistage-build/) approach, where python is used as a builder image (which then disposed by docker)

	FROM python:3.8.5-buster as builder
	
Among the obvious advantages of this approach is the greater and easier reproducibility. Even though, minikan re-uses packages downloaded from Apache Kafka project, rather than compiling them itself (for the moment).

Dockerization is done in two stages:

1. *python builder* will copy and run **automation** scripts
2. Produced Binary files will be picked up into the final image which will be tagged as the build result


### Docker commands

Image is build in a standard way, except that your current working folder must point to the project root. From that level `docker build` will have access to the full repository.

For example, In order to dockerize kafka broker you will need to run something like:
	
	git clone https://github.com/kafkanetes/minikan && cd minikan
	docker build -f images/kafka/Dockerfile -t kafkanetes/minikan-kafka:latest .

You can inspect the content of the produced image in a shell (w/o starting the broker):
	
	docker run -it kafkanetes/minikan-kafka:latest bash

You will find kafka files located under `/opt/kafka` which is what the ENV value of KAFKA_HOME is set to.

### Auto-dockerization with python

If you have basic *python3* installation (which means that `pip install automation/requirements.txt` is optional), the following:

	python dockerize.py

will print out bash-script commands that will:

- define all relevant versions
- contain the "docker build" commands to produce images (as discussed above)
- finally, with '--push' option there would be also a command that will try to upload the newest files in order to update content of the respective dockerhub.com repository.

Dockerization will produces the following images:

 - "builder" kafkanetes/minikan-buidler
 - "base" kafkanetes/minikan-base
 - "zk" kafkanetes/minikan-zk
 - "kafka" kafkanetes/minikan-kafka

FOr most cases the first two can be skipped if you want to explicitly re-run only particualr steps:

	python dockerize.py zk | bash
	python dockerize.py kafka | bash
	python dockerize.py base zk kafka | bash

If you are fine with the produced script, you can feed to the bash input pipe (optionally adding --push):

	python dockerize.py --push | bash

## Running in kubernetes

The **minikan** package has been developed and tested targeting *desktop docker* kubernetes.

### Deploying manifests

Manifests are deployed using:

	kubectl create namespace minikan # with the specific namespace
	kubectl config set-context $(kubectl config current-context) --namespace minikan #select namespace
	kubectl apply -R -f ./manifests/
	kubectl describe deploy/kan-kafka-1 

Inspect logs and observer the work of containers.

One convenient way to the pods inside the cluster for development purposes would be via port-forwarding tunnels. For that,
you need to run in parallel terminals:

	kubectl port-forward --address 0.0.0.0 svc/kan-kafka-1 :9092

You also need to update your /etc/hosts file with:

	127.0.0.1       kan-kafka-1.minikan


Note that for most operations direct connectivity to broker is enough. Zookeeper support is deprecated and will be replaced by the kafka protocol.
But if you still need zookeeper, then you also have an option run another port-forward:

	kubectl port-forward --address 0.0.0.0 svc/kan-zk-1 32181:2181


## Tests

See [tests/basic/README.md](tests/basic/REAME.md)


## Credit and Gratitude

It is worth to acknowledge work of communities and individuals behind the related open source projects. Their work and contribution is inspirational and deserves obvious credit.

- [Apache ZooKeeper](https://zookeeper.apache.org/)
- [Apache Kafka](https://kafka.apache.org/)
- [wurstmeister/kafka-docker](https://github.com/wurstmeister/kafka-docker/)

Thank you.