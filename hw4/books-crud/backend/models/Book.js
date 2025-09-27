const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Book = sequelize.define(
  'Book',
  {
    id: {
      type: DataTypes.INTEGER,
      autoIncrement: true,
      primaryKey: true,
    },
    title: {
      type: DataTypes.STRING(255),
      allowNull: false,
    },
    author: {
      type: DataTypes.STRING(255),
      allowNull: false,
    },
  },
  {
    tableName: 'books',
    timestamps: true,
  },
);

module.exports = Book;
