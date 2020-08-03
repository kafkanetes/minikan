ARG openjdk_version=11.0.8-jre-slim
ARG minikan_version=0.1.0
ARG vcs_ref=unspecified
ARG build_date=unspecified

FROM openjdk:${openjdk_version}

MAINTAINER kafkanetes

LABEL org.label-schema.name="minikan-base" \
      org.label-schema.description="kafkanetes - Base OpenJDK 11" \
      org.label-schema.build-date="${build_date}" \
      org.label-schema.vcs-url="https://github.com/kafkanetes/minikan" \
      org.label-schema.vcs-ref="${vcs_ref}" \
      org.label-schema.version="${minikan_version}_${openjdk_version}" \
      org.label-schema.schema-version="1.0" \
      maintainer="kafkanetes"

ENV MINIKAN_VERSION=$minikan_version \
    OPENJDK_VERSION=$openjdk_version

RUN apt-get update && apt-get install -y \
    curl \
    jq
