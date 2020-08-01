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
import re
import time
import logging
import requests
from pathlib import Path
from .shw import sh


DOWNLOAD_CHUNK_SIZE = 1024 * 1024

logger = logging.getLogger(__name__)


def download_file(url, file_path, attempts=3):
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


def convert_sha512_signature(filepath):
    """Looks like kafka files have a different SHA512 signature - convert it."""
    file_prefix = "{}:".format(Path(filepath).stem)
    with open(filepath) as f:
        lines = f.read().split("\n")
    sign = "".join(lines)
    sign = sign.replace(file_prefix, "")
    sign = re.sub("[\s]+", "", sign).lower()
    sign = "{} {}".format(sign, Path(filepath).stem) 
    with open(filepath, "w+") as f:
        f.write(sign)


class Builder(object):

    def __init__(self, config):
        self.config = config
    
    def unpack_archive(self, archive_path, extension=".tgz"):
        """Unpack kafka binaries if they are missing."""
        package_path = Path(str(archive_path)[:-1 * len(extension)])
        if not package_path.exists():
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
                        .format(package_path))
        assert package_path.exists() and package_path.is_dir()
        return package_path


class ZkBuilder(Builder):
    """Automate downloading and building of Apache Zookeeper."""

    @property
    def file_part(self):
        """Return base filename part."""
        return "apache-zookeeper-{zookeeper}"\
            .format(**self.config.versions)

    def download(self):
        """Download zookeeper binaries if they are missing."""
        archive_filename = f"{self.file_part}.tar.gz"
        zookeeper_version = self.config.versions.zookeeper
       
        local_path = Path(self.config.folders.download).joinpath(archive_filename)
        if not local_path.exists():
            logger.info("Download missing archive: {}".format(archive_filename))
            url = f"http://mirror.vorboss.net/apache/zookeeper/zookeeper-{zookeeper_version}/{archive_filename}"
            logger.info("Trying to download from mirror: {}".format(url))
            result_path = download_file(url, local_path)
            if not result_path:
                IOError(f"Failed to download: {archive_filename}")
        else:
            logger.info("Reusing existing archive: {}".format(local_path))
        return local_path        

    def verify(self):
        """Verify download."""
        archive_filename = f"{self.file_part}.tar.gz"
        dist_url = "https://www.apache.org/dist/zookeeper"
        zookeeper_version = self.config.versions.zookeeper
        signatures = {
            "keys": {"url": f"{dist_url}/KEYS"},
            "gpg": {"url": f"{dist_url}/zookeeper-{zookeeper_version}/{archive_filename}.asc"}, 
            "sha512": {"url": f"{dist_url}/zookeeper-{zookeeper_version}/{archive_filename}.sha512"},
        }
        for k in signatures:
            url = signatures[k]["url"]
            signatures[k]["local_path"] = Path(self.config.folders.download).joinpath(url[url.rindex("/") + 1:])
        signatures["keys"]["local_path"] = Path(self.config.folders.download).joinpath('ZK_KEYS')

        for k in signatures:
            s = signatures[k]
            if not s["local_path"].exists():
                logger.info("Download missing signature: {}".format(s["local_path"].name))
                if not download_file(s["url"], s["local_path"]):
                    raise IOError("Failed to download: {}".format(s["url"]))

        # check availability, again
        required_paths = [signatures[k]["local_path"] for k in signatures]
        required_paths += [Path(self.config.folders.download).joinpath(archive_filename)]
        for rp in required_paths:
            if not Path(rp).exists():
                raise IOError(f"Missing: {rp}")
        
        # Do verifications
        backup_workdir = os.getcwd()
        os.chdir(self.config.folders.download)
        logger.info("Verifying sha512 checksum")
        sha512sum = sh.sha512sum
        sha512sum('-c', signatures["sha512"]["local_path"].name)
        logger.info("Verifying gpg signature")
        gpg = sh.gpg
        gpg('--import', signatures["keys"]["local_path"].name)
        gpg('--verify', signatures["gpg"]["local_path"].name)
        os.chdir(backup_workdir)


class KafkaBuilder(Builder):
    """Automate downloading and building of Apache Kafka."""

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
            result_path = download_file(url, local_path)
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

    def verify(self):
        """Verify download."""
        archive_filename = "kafka_{scala}-{kafka}.tgz"\
            .format(**self.config.versions)
        kafka_version = self.config.versions.kafka
        dist_url = f"https://archive.apache.org/dist/kafka/{kafka_version}"
        signatures = {
            "keys": {"url": "https://archive.apache.org/dist/kafka/KEYS"},
            "gpg": {"url": f"{dist_url}/{archive_filename}.asc"}, 
            "sha512": {"url": f"{dist_url}/{archive_filename}.sha512"},
        }
        for k in signatures:
            url = signatures[k]["url"]
            signatures[k]["local_path"] = Path(self.config.folders.download).joinpath(url[url.rindex("/") + 1:])
        signatures["keys"]["local_path"] = Path(self.config.folders.download).joinpath('KAFKA_KEYS')

        for k in signatures:
            s = signatures[k]
            if not s["local_path"].exists():
                logger.info("Download missing signature: {}".format(s["local_path"].name))
                if not download_file(s["url"], s["local_path"]):
                    raise IOError("Failed to download: {}".format(s["url"]))

        # check availability, again
        required_paths = [signatures[k]["local_path"] for k in signatures]
        required_paths += [Path(self.config.folders.download).joinpath(archive_filename)]
        for rp in required_paths:
            if not Path(rp).exists():
                raise IOError(f"Missing: {rp}")
        
        # Do verifications
        backup_workdir = os.getcwd()
        os.chdir(self.config.folders.download)
        logger.info("Verifying sha512 checksum")
        convert_sha512_signature(signatures["sha512"]["local_path"])
        sha512sum = sh.sha512sum
        sha512sum('-c', signatures["sha512"]["local_path"].name)
        logger.info("Verifying gpg signature")
        gpg = sh.gpg
        gpg('--import', signatures["keys"]["local_path"].name)
        gpg('--verify', signatures["gpg"]["local_path"].name)
        os.chdir(backup_workdir)
