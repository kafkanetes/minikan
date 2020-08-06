import pytest
import random
import string
from kafka import KafkaConsumer, KafkaProducer, TopicPartition


BROKERS="kan-kafka-1.minikan:9092"

def random_string(length):
    return "".join(random.choice(string.ascii_letters) for i in range(length))


def test_kafka_producer_connectivity():
    # Test is based on https://github.com/dpkp/kafka-python/test/

    # compression = [None, 'gzip', 'snappy', 'lz4']
    compression = None

    producer = KafkaProducer(bootstrap_servers=BROKERS,
                             retries=5,
                             max_block_ms=30000,
                             compression_type=compression,
                             value_serializer=str.encode)
    consumer = KafkaConsumer(bootstrap_servers=BROKERS,
                             group_id=None,
                             consumer_timeout_ms=30000,
                             auto_offset_reset='earliest',
                             value_deserializer=bytes.decode)

    topic = random_string(5)

    messages = 100
    futures = []
    for i in range(messages):
        futures.append(producer.send(topic, 'msg %d' % i))
    ret = [f.get(timeout=30) for f in futures]
    assert len(ret) == messages
    producer.close()

    consumer.subscribe([topic])
    msgs = set()
    for i in range(messages):
        try:
            msgs.add(next(consumer).value)
        except StopIteration:
            break

    assert msgs == set(['msg %d' % (i,) for i in range(messages)])
    consumer.close()