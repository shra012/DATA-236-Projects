const kafka = require("kafka-node");

const kafkaHost = process.env.KAFKA_HOST || "localhost:9092";
const client = new kafka.KafkaClient({ kafkaHost });
const admin = new kafka.Admin(client);

const topics = [
  {
    topic: "request_topic",
    partitions: 1,
    replicationFactor: 1
  },
  {
    topic: "response_topic",
    partitions: 1,
    replicationFactor: 1
  }
];

admin.createTopics(topics, (err) => {
  if (err && !String(err.message).includes("already exists")) {
    console.error("Error creating topics", err);
    process.exitCode = 1;
    return;
  }

  if (err) {
    console.log("Topics already exist");
  } else {
    console.log("Topics created");
  }

  admin.listTopics((listErr, res) => {
    if (listErr) {
      console.error("Error listing topics", listErr);
      process.exitCode = 1;
    } else {
      const metadata = res?.[1]?.metadata || {};
      console.log("Available topics:", Object.keys(metadata).join(", "));
    }

    process.exit();
  });
});
