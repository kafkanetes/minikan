# minikan

Set up small-scale kafka cluster on local kubernetes - perfect for functionality testing and local development.

## Overview

**minikan**  stands for "mini" kafka-kubernetes (kan) and is a part of the [kafkanetes project](https://github.com/kafkanetes/).

Under small-scale kubernetes cluster - we mean "something" that can run on your local laptop using such products as Docker Desktop or minikube.

## Building docker images

Docker images are build using the [multi-stage]https://docs.docker.com/develop/develop-images/multistage-build/) approach, where python is used as a builder image as in 

	FROM python:3.8.5-buster as builder
	
Among the obvious advantages of this approach is the greater and easier reproducibility. Even though, minikan re-uses packages downloaded from Apache Kafka project, rather than compiling them itself (for the moment).


### Dockerize

In order to dockerize kafka broker you will need to run:

	docker build -f images/kafka/Dockerfile -t kafkanetes/minikan-kafka:latest .

You can inspect the content of the build image by running:
	
	docker run -it  kafkanetes/minikan-kafka:latest bash

