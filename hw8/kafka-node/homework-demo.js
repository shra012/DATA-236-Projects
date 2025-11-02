const KafkaClient = require("./client");

const REQUEST_TOPIC = process.env.REQUEST_TOPIC || "request_topic";
const client = new KafkaClient();

const state = {
  aliceId: null,
  bobId: null,
  charlieId: null
};

const steps = [
  {
    description: "Create user Alice",
    payload: {
      operation: "CREATE_USER",
      name: "Alice Smith",
      email: "alice@example.com",
      age: 25
    },
    onSuccess: (response) => {
      state.aliceId = response.userId;
    }
  },
  {
    description: "Create user Bob",
    payload: {
      operation: "CREATE_USER",
      name: "Bob Johnson",
      email: "bob@example.com",
      age: 30
    },
    onSuccess: (response) => {
      state.bobId = response.userId;
    }
  },
  {
    description: "Create user Charlie",
    payload: {
      operation: "CREATE_USER",
      name: "Charlie Davis",
      email: "charlie@example.com",
      age: 28
    },
    onSuccess: (response) => {
      state.charlieId = response.userId;
    }
  },
  {
    description: "List users after creation",
    payload: {
      operation: "LIST_USERS"
    }
  },
  {
    description: "Get Alice",
    payload: () => ({
      operation: "GET_USER",
      userId: state.aliceId
    })
  },
  {
    description: "Update Bob",
    payload: () => ({
      operation: "UPDATE_USER",
      userId: state.bobId,
      updates: {
        name: "Robert Johnson",
        age: 31
      }
    })
  },
  {
    description: "Delete Charlie",
    payload: () => ({
      operation: "DELETE_USER",
      userId: state.charlieId
    })
  },
  {
    description: "List users after deletion",
    payload: {
      operation: "LIST_USERS"
    }
  },
  {
    description: "Reject invalid email",
    payload: {
      operation: "CREATE_USER",
      name: "Invalid User",
      email: "not-an-email",
      age: 25
    },
    expectError: true
  },
  {
    description: "Reject negative age",
    payload: {
      operation: "CREATE_USER",
      name: "Invalid User",
      email: "test@example.com",
      age: -5
    },
    expectError: true
  },
  {
    description: "Reject duplicate email",
    payload: {
      operation: "CREATE_USER",
      name: "Another Alice",
      email: "alice@example.com",
      age: 30
    },
    expectError: true
  },
  {
    description: "Reject missing user",
    payload: {
      operation: "GET_USER",
      userId: "non-existent-id-12345"
    },
    expectError: true
  },
  {
    description: "Reject deleted user",
    payload: () => ({
      operation: "GET_USER",
      userId: state.charlieId
    }),
    expectError: true
  }
];

async function runDemo() {
  try {
    await delay(1000);

    for (const [index, step] of steps.entries()) {
      const payload =
        typeof step.payload === "function" ? step.payload() : step.payload;

      if (!payload) {
        throw new Error(`Missing payload for step ${index + 1}`);
      }

      try {
        const response = await makeRequest(payload, step.description);

        if (step.expectError) {
          throw new Error("Expected request to fail but it succeeded");
        }

        step.onSuccess?.(response);
      } catch (err) {
        if (step.expectError) {
          console.log(`${step.description} failed as expected: ${err.message}`);
        } else {
          throw err;
        }
      }
    }
  } catch (err) {
    console.error("Homework demo failed", err);
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
