
## Test zookeeper connectivity

1. start a port-forward in parallel terminal:
    
    kubectl port-forward --address 0.0.0.0 svc/kan-zk-1 32181:2181

    will output `Forwarding from 0.0.0.0:32181 -> 2181`

2. install prerequisites 

    pip install -r tests/basic/requirements.txt

3. run the test

    cd tests/basic && pytest

