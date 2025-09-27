const { Sequelize } = require('sequelize');
require('dotenv').config();

const dbName = process.env.DB_NAME || 'book_db';
const dbUser = process.env.DB_USER || 'root';
const dbPassword = process.env.DB_PASSWORD || '';
const dbHost = process.env.DB_HOST || 'localhost';
const dbPort = process.env.DB_PORT || 3306;

const sequelize = new Sequelize(dbName, dbUser, dbPassword, {
  host: dbHost,
  port: dbPort,
  dialect: 'mysql',
  logging: false,
});

const createDatabaseIfNotExists = async () => {
  const adminSequelize = new Sequelize('mysql', dbUser, dbPassword, {
    host: dbHost,
    port: dbPort,
    dialect: 'mysql',
    logging: false,
  });

  try {
    await adminSequelize.query(`CREATE DATABASE IF NOT EXISTS \`${dbName}\`;`);
  } finally {
    await adminSequelize.close();
  }
};

const testConnection = async () => {
  try {
    await sequelize.authenticate();
    console.log('Database connection ready');
  } catch (error) {
    console.error('Database connection failed', error.message);
    throw error;
  }
};

module.exports = { sequelize, testConnection, createDatabaseIfNotExists };
