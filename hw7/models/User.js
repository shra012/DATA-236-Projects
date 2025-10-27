// Lightweight in-memory replacement for a Mongoose User model used in tests
// Provides: constructor + save(), static findOne(), static create()

let _idCounter = 0;
const _users = [];

class User {
  constructor({ username, password, role, _id } = {}) {
    this._id = _id || String(++_idCounter);
    this.username = username;
    this.password = password;
    this.role = role || 'user';
  }

  save() {
    const existing = _users.find(u => u.username === this.username);
    if (!existing) {
      _users.push(this);
    } else {
      // update
      existing.password = this.password;
      existing.role = this.role;
    }
    return Promise.resolve(this);
  }

  static async findOne(query = {}) {
    if (query.username) {
      const found = _users.find(u => u.username === query.username);
      // return a plain User instance or null
      return found ? new User(found) : null;
    }
    return null;
  }

  static async create(obj = {}) {
    const u = new User(obj);
    _users.push(u);
    return u;
  }
}

module.exports = User;
