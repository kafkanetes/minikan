
## Test kafka connectivity and e2e message transport

1. start a port-forward in parallel terminal:
    
    kubectl port-forward --address 0.0.0.0 svc/kan-kafka-socat-1 9092:9092

    will output `Forwarding from 0.0.0.0:9092 -> 9092`

2. install prerequisites 

    pip install -r tests/basic/requirements.txt

3. run the test

    cd tests/basic && pytest test_kafka.py

## Test zookeeper connectivity

1. start a port-forward in parallel terminal:
    
    kubectl port-forward --address 0.0.0.0 svc/kan-zk-1 32181:2181

    will output `Forwarding from 0.0.0.0:32181 -> 2181`

2. install prerequisites 

    pip install -r tests/basic/requirements.txt

3. run the test

    cd tests/basic && pytest test_zk.py

