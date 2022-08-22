class MockKafkaProducer(object):
    """Mock for Kafka"""
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
        
mock_kafka_producer = MockKafkaProducer()
