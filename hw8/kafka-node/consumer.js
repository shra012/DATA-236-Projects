const kafka = require("kafka-node");
const crypto = require("crypto");

const KAFKA_HOST = process.env.KAFKA_HOST || "localhost:9092";
const REQUEST_TOPIC = process.env.REQUEST_TOPIC || "request_topic";
const RESPONSE_TOPIC = process.env.RESPONSE_TOPIC || "response_topic";

const userStore = new Map();

const client = new kafka.KafkaClient({ kafkaHost: KAFKA_HOST });
const consumer = new kafka.Consumer(
  client,
  [{ topic: REQUEST_TOPIC, partition: 0 }],
  { autoCommit: true }
);
const producer = new kafka.Producer(client);

producer.on("ready", () => {
  console.log("Kafka producer ready");
});

producer.on("error", (err) => {
  console.error("Kafka producer error", err);
});

consumer.on("error", (err) => {
  console.error("Kafka consumer error", err);
});

consumer.on("message", async (message) => {
  try {
    const envelope = JSON.parse(message.value);
    const { correlationId, replyTo, data } = envelope;

    if (!correlationId) {
      throw new Error("Missing correlationId in request");
    }

    if (!data || typeof data !== "object") {
      throw new Error("Request payload must be an object");
    }

    const responseTopic = replyTo || RESPONSE_TOPIC;
    const response = buildResponse(data);
    await sendResponse(responseTopic, {
      correlationId,
      data: response.data,
      error: response.error,
      processedAt: new Date().toISOString()
    });
  } catch (err) {
    console.error("Unable to process message", err);
  }
});

async function sendResponse(topic, message) {
  return new Promise((resolve, reject) => {
    producer.send(
      [
        {
          topic,
          messages: JSON.stringify(message),
          partition: 0
        }
      ],
      (err) => {
        if (err) {
          reject(err);
        } else {
          resolve();
        }
      }
    );
  });
}

function buildResponse(data) {
  try {
    return { data: handleOperation(data), error: null };
  } catch (err) {
    return { data: null, error: err.message };
  }
}

function handleOperation(data) {
  switch (data.operation) {
    case "CREATE_USER":
      return createUser(data);
    case "GET_USER":
      return getUser(data);
    case "UPDATE_USER":
      return updateUser(data);
    case "DELETE_USER":
      return deleteUser(data);
    case "LIST_USERS":
      return listUsers();
    default:
      throw new Error(`Unknown operation: ${data.operation}`);
  }
}

function createUser(data) {
  const { name, email, age } = data;

  if (!name || typeof name !== "string" || name.trim().length === 0) {
    throw new Error("Invalid name: must be a non-empty string");
  }

  if (!email || !validateEmail(email)) {
    throw new Error("Invalid email: must be a valid email format");
  }

  if (!Number.isInteger(age) || age <= 0) {
    throw new Error("Invalid age: must be a positive integer");
  }

  const normalizedEmail = email.trim().toLowerCase();
  for (const user of userStore.values()) {
    if (user.email === normalizedEmail) {
      throw new Error("User with this email already exists");
    }
  }

  const userId = generateUserId();
  const newUser = {
    userId,
    name: name.trim(),
    email: normalizedEmail,
    age,
    createdAt: new Date().toISOString()
  };

  userStore.set(userId, newUser);

  return {
    success: true,
    userId,
    message: "User created"
  };
}

function getUser(data) {
  const { userId } = data;

  if (!userId || typeof userId !== "string") {
    throw new Error("Invalid userId: must be a non-empty string");
  }

  const user = userStore.get(userId);

  if (!user) {
    throw new Error(`User not found: ${userId}`);
  }

  return {
    success: true,
    user: {
      userId: user.userId,
      name: user.name,
      email: user.email,
      age: user.age
    }
  };
}

function updateUser(data) {
  const { userId, updates } = data;

  if (!userId || typeof userId !== "string") {
    throw new Error("Invalid userId: must be a non-empty string");
  }

  if (!updates || typeof updates !== "object") {
    throw new Error("Invalid updates: must be an object");
  }

  const user = userStore.get(userId);

  if (!user) {
    throw new Error(`User not found: ${userId}`);
  }

  if (updates.name !== undefined) {
    if (typeof updates.name !== "string" || updates.name.trim().length === 0) {
      throw new Error("Invalid name: must be a non-empty string");
    }
    user.name = updates.name.trim();
  }

  if (updates.email !== undefined) {
    if (!validateEmail(updates.email)) {
      throw new Error("Invalid email: must be a valid email format");
    }

    const normalizedEmail = updates.email.trim().toLowerCase();
    for (const [id, existingUser] of userStore.entries()) {
      if (id !== userId && existingUser.email === normalizedEmail) {
        throw new Error("Email already in use by another user");
      }
    }

    user.email = normalizedEmail;
  }

  if (updates.age !== undefined) {
    if (!Number.isInteger(updates.age) || updates.age <= 0) {
      throw new Error("Invalid age: must be a positive integer");
    }
    user.age = updates.age;
  }

  user.updatedAt = new Date().toISOString();
  userStore.set(userId, user);

  return {
    success: true,
    user: {
      userId: user.userId,
      name: user.name,
      email: user.email,
      age: user.age
    }
  };
}

function deleteUser(data) {
  const { userId } = data;

  if (!userId || typeof userId !== "string") {
    throw new Error("Invalid userId: must be a non-empty string");
  }

  const user = userStore.get(userId);

  if (!user) {
    throw new Error(`User not found: ${userId}`);
  }

  userStore.delete(userId);

  return {
    success: true,
    message: "User deleted"
  };
}

function listUsers() {
  const users = Array.from(userStore.values()).map((user) => ({
    userId: user.userId,
    name: user.name,
    email: user.email,
    age: user.age
  }));

  return {
    success: true,
    users,
    count: users.length
  };
}

function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function generateUserId() {
  if (typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }

  return crypto.randomBytes(16).toString("hex");
}

process.on("SIGINT", () => {
  consumer.close(true, () => {
    process.exit(0);
  });
});

console.log(`Kafka consumer listening on topic "${REQUEST_TOPIC}"`);
