# builder stage
ARG minikan_version=latest
FROM kafkanetes/minikan-builder:${minikan_version} as builder
COPY . /root
WORKDIR /root
RUN python minikan build zk

# zk image
ARG minikan_version=latest
FROM kafkanetes/minikan-base:${minikan_version}
MAINTAINER kafkanetes
# more args
ARG zookeeper_version=3.6.1
ARG vcs_ref=unspecified
ARG build_date=unspecified

LABEL org.label-schema.name="minikan-zk" \
      org.label-schema.description="kafkanetes - Apache Zookeeper" \
      org.label-schema.build-date="${build_date}" \
      org.label-schema.vcs-url="https://github.com/kafkanetes/minikan" \
      org.label-schema.vcs-ref="${vcs_ref}" \
      org.label-schema.version="${minikan_version}_${zookeeper_version}" \
      org.label-schema.schema-version="1.0" \
      maintainer="kafkanetes"

ENV MINIKAN_VERSION=$minikan_version \
    ZOOKEEPER_VERSION=$zookeeper_version \
    ZK_HOME=/opt/zk

ENV PATH=${PATH}:${ZK_HOME}/bin

RUN apt-get update && apt-get install -y \
    curl \
    jq

COPY --from=builder /root/download/apache-zookeeper-${ZOOKEEPER_VERSION}-bin /opt/zk-${ZOOKEEPER_VERSION}
RUN ln -s /opt/zk-${ZOOKEEPER_VERSION} ${ZK_HOME} \
    && mv ${ZK_HOME}/conf/zoo_sample.cfg ${ZK_HOME}/conf/zoo.cfg \
    && sed -i "s|/tmp/zookeeper|$ZK_HOME/data|g" ${ZK_HOME}/conf/zoo.cfg \
    && mkdir ${ZK_HOME}/data
COPY ./images/zk/* ${ZK_HOME}/bin/

WORKDIR  ${ZK_HOME}

EXPOSE 2181 2888 3888

CMD ["start-zk.sh"]
