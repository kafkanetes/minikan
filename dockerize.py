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


def get_kan_zk_version(params):
    """Return zookeeper docker image version."""
    return "{minikan_version}_{zookeeper_version}".format(**params)


def get_kan_kafka_version(params):
    """Return kafka docker image version."""
    return "{minikan_version}_{scala_version}_{kafka_version}".format(**params)


def _build_zk(params):
    return """# Build zookeeper image
docker build \
-f images/zk/Dockerfile \
-t kafkanetes/minikan-zk:{kan_zk_version} \
--build-arg build_date="{build_date}" \
--build-arg minikan_version={minikan_version} \
--build-arg zookeeper_version={zookeeper_version} \
.
""".format(**params)

def _build_kafka(params):
    return """# Build kafka image
docker build \
-f images/kafka/Dockerfile \
-t kafkanetes/minikan-kafka:{kan_kafka_version} \
--build-arg build_date="{build_date}" \
--build-arg minikan_version={minikan_version} \
--build-arg scala_version={scala_version} \
--build-arg kafka_version={kafka_version} \
.
""".format(**params)


def print_build_cmds(cliargs, params):
    """Generate bash-code with `docker build` commands."""
    print("""set -e
set echo off
echo "minikan dockerization - Start"
""")

    if "all" in cliargs or "zk" in cliargs:
        print(_build_zk(params))

    if "all" in cliargs or "kafka" in cliargs:
        print(_build_kafka(params))

    print("""echo "minikan dockerization - Done"
echo
echo Review produced images:
docker images kafkanetes/minikan-zk | head
docker images kafkanetes/minikan-kafka | head
echo
echo Optionally, inspect image content by running:
echo docker run -it kafkanetes/minikan-zk:{kan_zk_version} bash
echo docker run -it kafkanetes/minikan-kafka:{kan_kafka_version} bash
""".format(**params))
    # Optionally, upload images
    if "--push" in cliargs:
        print("""set echo off
echo "Upload minikan docker images"
# docker push
""".format(**params))


##
# Main
#

# args
if len(sys.argv) > 1:
    cliargs = sys.argv[1:]
else:
    cliargs = ["all"]
# params
params = {k.lower(): getattr(versions, k)
        for k in dir(versions)
        if not k.startswith('__')}
params['build_date'] = get_build_date()
params['kan_zk_version'] = get_kan_zk_version(params)
params['kan_kafka_version'] = get_kan_kafka_version(params)
# print bash
print_build_cmds(cliargs, params)
