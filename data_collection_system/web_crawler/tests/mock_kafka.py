class MockKafkaProducer(object):
    """Mock for Kafka producer"""
    def __init__(self, bootstrap_servers='140.113.73.56:9092', linger_ms=1000, batch_size=1000) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.linger_ms = linger_ms
        self.batch_size = batch_size
        self.data = {}

    def send(self, topic: str, message: str) -> None:
        """Mock for sending the message on topic"""
        print(topic, message)
        if topic not in self.data:
            self.data[topic] = []
        self.data[topic].append(message)

class MockMessage(object):
    """Mock for kafka massage"""
    def __init__(self,value:str, topic:str=None, key:str=None) -> None:
        self.topic = topic
        self.key = key
        self.value = value

mock_kafka_producer = MockKafkaProducer()
