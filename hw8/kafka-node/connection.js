const kafka = require("kafka-node");

const DEFAULT_KAFKA_HOST = process.env.KAFKA_HOST || "localhost:9092";

class ConnectionProvider {
  constructor(kafkaHost = DEFAULT_KAFKA_HOST) {
    this.kafkaHost = kafkaHost;
    this.kafkaProducerConnection = null;
  }

  getConsumer(topicName) {
    if (typeof topicName !== "string" || topicName.length === 0) {
      throw new Error("topicName must be a non-empty string");
    }

    const client = new kafka.KafkaClient({ kafkaHost: this.kafkaHost });

    client.on("error", (err) => {
      console.error("Kafka client error:", err);
    });

    return new kafka.Consumer(
      client,
      [{ topic: topicName, partition: 0 }],
      {
        autoCommit: true,
        fetchMaxWaitMs: 1000,
        fetchMaxBytes: 1024 * 1024
      }
    );
  }

  getProducer() {
    if (!this.kafkaProducerConnection) {
      const client = new kafka.KafkaClient({ kafkaHost: this.kafkaHost });
      this.kafkaProducerConnection = new kafka.HighLevelProducer(client);

      this.kafkaProducerConnection.on("error", (err) => {
        console.error("Producer error:", err);
      });
    }
    return this.kafkaProducerConnection;
  }
}

module.exports = new ConnectionProvider();
