const express = require("express");
const router = express.Router();
const bcrypt = require("bcryptjs");

const users = [
  {
    id: 1,
    username: "admin",
    password: bcrypt.hashSync("password", 8),
    fullName: "Administrator",
    role: "admin",
  },
  {
    id: 2,
    username: "student1",
    password: bcrypt.hashSync("ads2025", 8),
    fullName: "John Doe",
    role: "student",
  },
  {
    id: 3,
    username: "faculty",
    password: bcrypt.hashSync("sjsu2025", 8),
    fullName: "Dr. Jane Smith",
    role: "faculty",
  },
];

router.get("/login", (req, res) => {
  if (req.session.user) {
    return res.redirect("/");
  }
  res.render("login", { error: null });
});

router.post("/login", (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.render("login", {
      error: "Please provide both username and password.",
    });
  }

  const user = users.find((u) => u.username === username);

  if (user && bcrypt.compareSync(password, user.password)) {
    req.session.user = {
      id: user.id,
      username: user.username,
      fullName: user.fullName,
      role: user.role,
    };
    console.log(`User ${user.username} logged in successfully`);
    res.redirect("/");
  } else {
    console.log(`Failed login attempt for username: ${username}`);
    res.render("login", { error: "Invalid username or password." });
  }
});

router.get("/logout", (req, res) => {
  if (req.session.user) {
    console.log(`User ${req.session.user.username} logged out`);
  }

  req.session.destroy((err) => {
    if (err) {
      console.error("Error destroying session:", err);
      return res.redirect("/");
    }
    res.redirect("/");
  });
});

module.exports = router;
