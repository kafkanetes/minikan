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

If you are fine with the produced script, you can feed to the bash input pipe:

	python dockerize.py --push | bash

