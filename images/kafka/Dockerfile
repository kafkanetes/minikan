# args
ARG minikan_version=0.1.0
ARG scala_version=2.13
ARG kafka_version=2.5.0
ARG vcs_ref=unspecified
ARG build_date=unspecified

# builder stage
FROM kafkanetes/minikan-builder:${minikan_version} as builder
COPY . /root
WORKDIR /root
RUN python minikan build kafka

# kafka image
FROM kafkanetes/minikan-base:${minikan_version}
MAINTAINER kafkanetes

LABEL org.label-schema.name="minikan-kafka" \
      org.label-schema.description="kafkanetes - Apache Kafka" \
      org.label-schema.build-date="${build_date}" \
      org.label-schema.vcs-url="https://github.com/kafkanetes/minikan" \
      org.label-schema.vcs-ref="${vcs_ref}" \
      org.label-schema.version="${minikan_version}_${scala_version}_${kafka_version}" \
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

WORKDIR ${KAFKA_HOME}

EXPOSE 9092

CMD ["start-kafka.sh"]
