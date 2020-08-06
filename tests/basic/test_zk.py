from kazoo.client import KazooClient

# HOSTS="127.0.0.1:2181"
HOSTS="0.0.0.0:32181"


def test_connectivity():
    # Create a client and start it
    zk = KazooClient(hosts=HOSTS)
    zk.start()

    # Now you can do the regular zookepper API calls
    # Ensure some paths are created required by your application
    zk.ensure_path("/test/foo/bar") 

    # In the end, stop it
    zk.stop()
