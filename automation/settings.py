"""Default settings used by the automation scripts."""
from box import Box
from copy import deepcopy
from pathlib import Path
from .versions import (MINIKAN_VERSION, SCALA_VERSION, KAFKA_VERSION,
                       ZOOKEEPER_VERSION)


PACKAGE_PATH = Path(__file__).resolve().parent
DOWNLOAD_FOLDER = PACKAGE_PATH.parent.joinpath('download')


Defaults = {
    'folders': {
        'download': DOWNLOAD_FOLDER,
    },
    'versions': {
        'minikan': MINIKAN_VERSION,
        'scala': SCALA_VERSION,
        'kafka': KAFKA_VERSION,
        'zookeeper': ZOOKEEPER_VERSION,
    },
}


def load_config(custom=None):
    """Load config"""
    values = deepcopy(Defaults)

    # Optionally, extend with other configurations, e.g. passed from CLI.
    if custom is not None:
        values.update()

    # Wrap into object-like behavior
    return Box(values)
