const crypto = require("crypto");
const connection = require("./connection");

const RESPONSE_TOPIC = process.env.RESPONSE_TOPIC || "response_topic";

const parsedTimeout = Number(process.env.KAFKA_RPC_TIMEOUT);
const REQUEST_TIMEOUT_MS =
  Number.isFinite(parsedTimeout) && parsedTimeout > 0 ? parsedTimeout : 8000;

class KafkaRPC {
  constructor(connectionProvider = connection) {
    this.connection = connectionProvider;
    this.pendingRequests = new Map();
    this.producer = this.connection.getProducer();
    this.responseQueueReady = false;
  }

  makeRequest(topicName, content, callback) {
    if (typeof topicName !== "string" || topicName.length === 0) {
      throw new Error("topicName must be a non-empty string");
    }

    if (typeof callback !== "function") {
      throw new Error("callback must be a function");
    }

    this.ensureResponseQueue();

    const correlationId = crypto.randomBytes(16).toString("hex");
    const timeoutId = setTimeout(() => {
      this.resolveRequest(correlationId, new Error("Request timeout"), null);
    }, REQUEST_TIMEOUT_MS);

    this.pendingRequests.set(correlationId, { callback, timeoutId });

    const payload = [
      {
        topic: topicName,
        messages: JSON.stringify({
          correlationId,
          replyTo: RESPONSE_TOPIC,
          data: content,
          timestamp: new Date().toISOString()
        }),
        partition: 0
      }
    ];

    this.producer.send(payload, (err) => {
      if (err) {
        clearTimeout(timeoutId);
        this.pendingRequests.delete(correlationId);
        callback(err, null);
      }
    });
  }

  ensureResponseQueue() {
    if (this.responseQueueReady) {
      return;
    }

    const consumer = this.connection.getConsumer(RESPONSE_TOPIC);

    consumer.on("message", (message) => {
      try {
        const response = JSON.parse(message.value);
        const { correlationId, data, error } = response;

        if (!correlationId) {
          return;
        }

        if (!this.pendingRequests.has(correlationId)) {
          return;
        }

        if (error) {
          this.resolveRequest(correlationId, new Error(error), null);
        } else {
          this.resolveRequest(correlationId, null, data);
        }
      } catch (err) {
        console.error("Unable to parse response message", err);
      }
    });

    consumer.on("error", (err) => {
      console.error("Response consumer error", err);
    });

    this.responseQueueReady = true;
  }

  resolveRequest(correlationId, error, data) {
    const entry = this.pendingRequests.get(correlationId);

    if (!entry) {
      return;
    }

    clearTimeout(entry.timeoutId);
    this.pendingRequests.delete(correlationId);
    entry.callback(error, data);
  }
}

module.exports = KafkaRPC;
