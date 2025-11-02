const RPC = require("./rpc");

class KafkaClient {
  constructor(rpcInstance = new RPC()) {
    this.rpc = rpcInstance;
  }

  makeRequest(queueName, payload, callback) {
    if (typeof queueName !== "string" || queueName.length === 0) {
      throw new Error("queueName must be a non-empty string");
    }

    this.rpc.makeRequest(queueName, payload, callback);
  }
}

module.exports = KafkaClient;
