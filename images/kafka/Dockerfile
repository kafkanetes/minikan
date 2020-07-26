FROM python:3.8.5-buster as builder

COPY . /root
WORKDIR /root

RUN pip install -r automation/requirements.txt \
	&& python minikan build kafka

FROM openjdk:11.0.8-jre-slim
MAINTAINER kafkanetes

ARG minikan_version=0.1.0
ARG kafka_version=2.5.0
ARG scala_version=2.13
ARG vcs_ref=unspecified
ARG build_date=unspecified

LABEL org.label-schema.name="minikan-kafka" \
      org.label-schema.description="kafkanetes - Apache Kafka broker" \
      org.label-schema.build-date="${build_date}" \
      org.label-schema.vcs-url="https://github.com/kafkanetes/minikan" \
      org.label-schema.vcs-ref="${vcs_ref}" \
      org.label-schema.version="${scala_version}_${kafka_version}" \
      org.label-schema.schema-version="1.0" \
      maintainer="kafkanetes"

ENV MINIKAN_VERSION=$minikan_version \
	KAFKA_VERSION=$kafka_version \
    SCALA_VERSION=$scala_version \
    KAFKA_HOME=/opt/kafka

ENV PATH=${PATH}:${KAFKA_HOME}/bin

RUN apt-get update && apt-get install -y \
    curl \
    jq

RUN ln -s /opt/kafka_${SCALA_VERSION}-${KAFKA_VERSION} ${KAFKA_HOME}

COPY --from=builder /root/download/kafka_${SCALA_VERSION}-${KAFKA_VERSION} /opt/kafka_${SCALA_VERSION}-${KAFKA_VERSION}

COPY ./images/kafka/* ${KAFKA_HOME}/bin/

CMD ["start-kafka.sh"]
