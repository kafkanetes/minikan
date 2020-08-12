<p align="center">
  <a href="https://github.com/kafkanetes/">
    <img src="/doc/img/logo.png?raw=true" width="200"/>
  </a>
</p>


# minikan

Set up a small-scale kafka cluster on local kubernetes - perfect for functionality testing and local development.

> TL;DR - how to stand up kafkanetes minikan <3

<p align="center"><img src="/doc/img/demo.gif?raw=true"/></p>

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

	python dockerize.py builder all

Note that  `all = all images w/o builder`, but you don't need to rebuild builder that frequently for the 2-stage building Dockerfiles.

The above will print out bash-script commands that will:

- define all relevant versions
- contain the "docker build" commands to produce images (as discussed above)
- finally, with '--push' option there would be also a command that will try to upload the newest files in order to update content of the respective dockerhub.com repository.

Dockerization will produces the following images:

 - "builder" kafkanetes/minikan-buidler
 - "base" kafkanetes/minikan-base
 - "zk" kafkanetes/minikan-zk
 - "kafka" kafkanetes/minikan-kafka

For most cases the first two can be skipped if you want to explicitly re-run only particualr steps:

	python dockerize.py builder all | bash  # results in building all images starting with builder
	python dockerize.py | bash  # results in building all images except builder
	python dockerize.py base zk kafka | bash  # only base
	python dockerize.py zk | bash  # only zookeeper
	python dockerize.py kafka | bash  # only kafka

If you are fine with the produced script, you can feed to the bash input pipe (optionally adding --push):

	python dockerize.py --push | bash

## Running in kubernetes

The **minikan** package has been developed and tested targeting *desktop docker* kubernetes.

### Deploying manifests

Manifests are deployed using:

	kubectl create namespace minikan # with the specific namespace
	kubectl config set-context $(kubectl config current-context) --namespace minikan #select namespace
	kubectl apply -R -f ./manifests/latest
	kubectl describe deploy/kan-kafka-1 

After playing the manifests, you might want to inspect logs and observe the work of containers. There should be no visible errors.

### Connecting to kafka

> bootstrap.servers=kan-kafka-1.minikan:9092

1. For the above to work, you might want to update your /etc/hosts file with:

	127.0.0.1       kan-kafka-1.minikan

This is required since `kan-kafka-1.minikan` is an ADVERTISED_LISTENER (domain `minikan` equals to kubernetes namespace where the minikan manifests are deployed). So this host will be reported as a part of the kafka metadata (refreshed approximately every 20s, but in our case - always equals to a single broker for the simplest scenario).

(On WSL you might have this file auto-regenerated per reboot).

2. You also need to expose 9092 port on your local machine

One convenient way to connect the pods inside the cluster for development purposes would be via port-forwarding tunnels. For that,
you need to run in parallel terminals:

	kubectl port-forward --address 0.0.0.0 svc/kan-kafka-socat-1 9092:9092

The above will connect to the [socat wiring](https://hub.docker.com/r/alpine/socat/) - tiny alpine-based tcp forwarding service that continuously listens and reroutes TCP traffic within kubernetes namespace where brokers are deployed. In terms of networking, this is one of the most elegant approaches compared to NodePort, LoadBalancer, L4-ingress proxies, firewall bypasses, etc. It is well suited for running kubernetes in the local environment (such as Docker Desktop - for comparison see [how to expose ports via docker-compose](https://techcommunity.microsoft.com/t5/windows-dev-appconsult/first-steps-with-docker-and-kubernetes-introduction/ba-p/357525)).


### Connecting to zookeeper

Note that for most operations direct connectivity to broker is enough. Zookeeper support is deprecated and will be replaced by the kafka protocol.
But if you still need zookeeper, then you also have an option run another port-forward:

	kubectl port-forward --address 0.0.0.0 svc/kan-zk-1 32181:2181


## Tests

See [tests/basic/README.md](tests/basic/README.md)


## Credit and Gratitude

It is worth to acknowledge work of communities and individuals behind the related open source projects. Their work and contribution is inspirational and deserves obvious credit.

- [Apache ZooKeeper](https://zookeeper.apache.org/)
- [Apache Kafka](https://kafka.apache.org/)
- [wurstmeister/kafka-docker](https://github.com/wurstmeister/kafka-docker/)

Thank you.