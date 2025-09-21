require("dotenv").config();
const express = require("express");
const session = require("express-session");
const bodyParser = require("body-parser");
const path = require("path");
const crypto = require("crypto");
const authRouter = require("./auth");

const app = express();
const PORT = process.env.PORT || 3000;

const generateSessionSecret = () => {
  if (process.env.SESSION_SECRET) {
    return process.env.SESSION_SECRET;
  }

  const salt = crypto.randomBytes(32).toString("hex");
  const baseString = "MSADI-auth-system-" + Date.now();
  const hash = crypto
    .createHmac("sha256", salt)
    .update(baseString)
    .digest("hex");

  console.log(
    "Generated secure session secret. Set SESSION_SECRET in environment for production."
  );
  return salt + hash;
};

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.use((req, res, next) => {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("X-XSS-Protection", "1; mode=block");
  res.setHeader("Referrer-Policy", "strict-origin-when-cross-origin");
  next();
});

app.use(
  session({
    secret: generateSessionSecret(),
    resave: false,
    saveUninitialized: false,
    rolling: true,
    name: "ads.session.id",
    cookie: {
      secure: process.env.NODE_ENV === "production",
      httpOnly: true,
      maxAge: 60 * 60 * 1000,
      sameSite: "strict",
    },
  })
);

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

function requireAuth(req, res, next) {
  if (!req.session.user) {
    return res.redirect("/login");
  }
  next();
}

app.get("/", (req, res) => {
  res.render("index", { user: req.session.user });
});

app.get("/dashboard", requireAuth, (req, res) => {
  res.render("dashboard", { user: req.session.user });
});

app.use("/", authRouter);

app.use((req, res) => {
  res.status(404).send(`
        <div style="text-align: center; margin-top: 50px; font-family: Arial, sans-serif;">
            <h1>404 - Page Not Found</h1>
            <p>The requested page does not exist.</p>
            <a href="/" style="color: #007bff; text-decoration: none;">Return to Home</a>
        </div>
    `);
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send("Something broke!");
});

app.listen(PORT, () => {
  console.log(
    `MSADI Authentication Server is running on http://localhost:${PORT}`
  );
  console.log("Department of Applied Data Science");
});
