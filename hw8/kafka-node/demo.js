const KafkaClient = require("./client");

const REQUEST_TOPIC = process.env.REQUEST_TOPIC || "request_topic";
const client = new KafkaClient();

async function runDemo() {
  try {
    await delay(1000);

    await makeRequest(
      {
        operation: "LIST_USERS"
      },
      "Listing existing users"
    );

    const created = await makeRequest(
      {
        operation: "CREATE_USER",
        name: "Demo User",
        email: "demo@example.com",
        age: 30
      },
      "Creating a demo user"
    );

    await makeRequest(
      {
        operation: "GET_USER",
        userId: created.userId
      },
      "Retrieving the created user"
    );

    await makeRequest(
      {
        operation: "DELETE_USER",
        userId: created.userId
      },
      "Deleting the created user"
    );
  } catch (err) {
    console.error("Demo failed", err);
    process.exitCode = 1;
  } finally {
    process.exit();
  }
}

function makeRequest(payload, description) {
  return new Promise((resolve, reject) => {
    console.log(description);
    client.makeRequest(REQUEST_TOPIC, payload, (err, response) => {
      if (err) {
        reject(err);
        return;
      }

      if (response && response.error) {
        reject(new Error(response.error));
        return;
      }

      console.log("Response:", response);
      resolve(response);
    });
  });
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

runDemo();

process.on("uncaughtException", (err) => {
  console.error("Uncaught exception", err);
  process.exit(1);
});

process.on("SIGINT", () => {
  process.exit(0);
});
