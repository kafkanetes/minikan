FROM python:3.8.5-buster

ARG minikan_version=0.1.0
ARG vcs_ref=unspecified
ARG build_date=unspecified

LABEL org.label-schema.name="minikan-builder" \
      org.label-schema.description="kafkanetes - Builder" \
      org.label-schema.build-date="${build_date}" \
      org.label-schema.vcs-url="https://github.com/kafkanetes/minikan" \
      org.label-schema.vcs-ref="${vcs_ref}" \
      org.label-schema.version="${minikan_version}" \
      org.label-schema.schema-version="1.0" \
      maintainer="kafkanetes"

WORKDIR /root
RUN mkdir automation
COPY automation/requirements.txt /root/automation/
RUN pip install -r automation/requirements.txt
