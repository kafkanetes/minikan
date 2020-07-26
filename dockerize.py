#!/usr/bin/env python
"""
Run this low-dependency python script to generate dockerization bash-commands.

Script can output bash-code that will:

- define all relevant versions
- generate docker files
- run "docker build" commands to produce images
- publish new images to dockerhub

See `README.md` for detailed explanation.
"""
import sys
import datetime
from automation import versions


if __name__ != '__main__':
    raise Exception("Can be run only directly")

##
# Help
#
if "-h" in sys.argv or "--help" in sys.argv:
    print("""Dockerize minikan kafka and zookeeper

Usage examples:

1. `python dockerize.py`         -  prints out bash-code to do dockerization;
2. `python dockerize.py`         -  same as above but contains "docker push" commands;
3. `python dockerize.py | bash`  -  runs the bash-code"
""")
    exit(1)


def get_build_date():
    """Return now formatted according to RFC 3339."""
    d = datetime.datetime.utcnow()
    return d.isoformat("T") + "Z"


def get_kan_zk_version(vars):
    """Return zookeeper docker image version."""
    return "{minikan_version}_{scala_version}_{zookeeper_version}".format(**vars)


def get_kan_kafka_version(vars):
    """Return kafka docker image version."""
    return "{minikan_version}_{scala_version}_{kafka_version}".format(**vars)


def print_build_cmds(vars):
    """Generate bash-code with `docker build` commands."""
    print("""set -e
set echo off
echo "minikan dockerization - Start"

# Build zookeeper image
# docker build -f images/zk/Dockerfile -t kafkanetes/minikan-zk:latest .

# Build kafka image
docker build \
-f images/kafka/Dockerfile \
-t kafkanetes/minikan-kafka:{kan_kafka_version} \
--build-arg build_date="{build_date}" \
--build-arg minikan_version={minikan_version} \
--build-arg scala_version={scala_version} \
--build-arg kafka_version={kafka_version} \
.

echo "minikan dockerization - Done"
echo
echo Review produced images:
docker images kafkanetes/minikan-kafka | head
echo
echo Optionally, inspect image content by running:
echo docker run -it kafkanetes/minikan-kafka:{kan_kafka_version} bash
""".format(**vars))
    # Optionally, upload images
    if "--push" in sys.argv:
        print("""set echo off
echo "Upload minikan docker images"
# docker push
""".format(**vars))


##
# Main
#
vars = {k.lower(): getattr(versions, k)
        for k in dir(versions)
        if not k.startswith('__')}
vars['build_date'] = get_build_date()
vars['kan_zk_version'] = get_kan_zk_version(vars)
vars['kan_kafka_version'] = get_kan_kafka_version(vars)

print_build_cmds(vars)
