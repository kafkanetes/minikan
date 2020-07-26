"""
Help with file download when building kafka and zookeeper docker images.

This will:

    - download software archive
    - verify archive signature
    - unpack the archive content into the download folder

For the rest of the multi-stage docker building process
see `images/kafka/Dockerfile` and `images/zk/Dockerfile`.

For exact versions - see `automation/versions.py`
                     and `automation/settings.py`.

"""
import os
import time
import logging
import requests
from pathlib import Path
from .shw import sh


DOWNLOAD_CHUNK_SIZE = 1024 * 1024

logger = logging.getLogger(__name__)


def download_archive(url, file_path, attempts=3):
    """Download file in the URL into downloads path."""
    if not file_path:
        file_path = url.split('/')[-1]
    download_folder = Path(file_path).parent
    if not download_folder.exists():
        logger.info(f"Create missing folder: {download_folder}")
        download_folder.mkdir(parents=True, exist_ok=True)

    logger.info(f'Downloading {url} content to {file_path}')
    if not url.startswith("http://") and not url.startswith("https://"):
        raise Exception("Wrong URL - missing HTTP(S) scheme prefix: ", url)
    for attempt in range(1, attempts + 1):
        try:
            if attempt > 1:
                time.sleep(10)  # 10 seconds wait time between downloads
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                with open(file_path, 'wb') as out_file:
                    # Iterate over 1MB chunks
                    for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                        out_file.write(chunk)
                logger.info('Download finished successfully')
                return file_path
        except Exception as ex:
            logger.error(f'Attempt #{attempt} failed with error: {ex}')
    return ''


class KafkaBuilder(object):

    def __init__(self, config):
        self.config = config

    def _get_mirror_url(self, archive_filename):
        url = "https://www.apache.org/dyn/closer.cgi?path=/kafka/"
        url += "{kafka}/{archive}&as_json=1"\
            .format(archive=archive_filename, **self.config.versions)

        r = requests.get(url)
        if r.status_code != 200:
            return ''
        mirror = r.json()
        return "{preferred}{path_info}".format(**mirror)

    def download(self):
        """Download kafka binaries if they are missing."""
        archive_filename = "kafka_{scala}-{kafka}.tgz"\
            .format(**self.config.versions)

        local_path = Path(self.config.folders.download).joinpath(archive_filename)
        if not local_path.exists():
            logger.info("Download missing archive: {}".format(archive_filename))
            # url = "https://archive.apache.org/dist/kafka/{}/{}"\
            #     .format(config.versions.kafka, archive_filename)
            url = self._get_mirror_url(archive_filename)
            logger.info("Trying to download from mirror: {}".format(url))
            result_path = download_archive(url, local_path)
            if not result_path:
                logger.error("Failed to download from preferred mirror: {}"
                             .format(url))
                fallback_url = "https://archive.apache.org/dist/kafka/{kafka}/{archive}"\
                    .format(archive=archive_filename, **self.config.versions)
                result_path = download_archive(fallback_url, local_path)
            if not result_path:
                raise IOError("Failed to download archive.")
        else:
            logger.info("Reusing existing archive: {}".format(local_path))
        return local_path

    def unpack(self, archive_path):
        """Unpack kafka binaries if they are missing."""
        kafka_path = Path(str(archive_path)[:-4])  # cut .tgz
        if not kafka_path.exists():
            logger.info("Unpack {}".format(archive_path))
            backup_workdir = os.getcwd()
            os.chdir(self.config.folders.download)
            # Pythonize some cli-commands
            tar = sh.tar
            res = tar('xf', str(archive_path))
            for line in res.split("\n"):
                if not line:
                    continue
                logger.info("unpack - " + line)
            os.chdir(backup_workdir)
        else:
            logger.info("Destination is already present or previously unpacked: {}"
                        .format(kafka_path))
        assert kafka_path.exists() and kafka_path.is_dir()
        return kafka_path
