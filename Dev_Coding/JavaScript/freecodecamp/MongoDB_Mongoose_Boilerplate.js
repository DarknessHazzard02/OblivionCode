/**
 * MongoDB + Mongoose Boilerplate - freeCodeCamp Back End APIs
 *
 * Concepts: Schema definition, model creation, CRUD operations,
 *           validators, virtuals, middleware (hooks), query methods,
 *           population (relationships), indexing
 *
 * This file documents and simulates Mongoose patterns.
 * In production: const mongoose = require('mongoose')
 */

console.log("=== MongoDB + Mongoose Boilerplate Demo ===\n");

// ─── 1. Schema Definition ─────────────────────────────────────────────────────
console.log("1) Schema definition examples:\n");

const userSchemaCode = `
const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  // String with validation
  name: {
    type: String,
    required: [true, 'Name is required'],
    trim: true,
    minlength: 2,
    maxlength: 50,
  },

  // Email with regex validation
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    match: [/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/, 'Invalid email format'],
  },

  // Enum field
  role: {
    type: String,
    enum: ['user', 'admin', 'moderator'],
    default: 'user',
  },

  // Number with min/max
  age: { type: Number, min: 0, max: 150 },

  // Nested object
  address: {
    street: String,
    city: String,
    country: { type: String, default: 'US' },
  },

  // Array of strings
  hobbies: [String],

  // Reference to another model (relationship)
  createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },

  // Timestamps
  createdAt: { type: Date, default: Date.now },
  isActive: { type: Boolean, default: true },
}, {
  timestamps: true,  // auto-adds createdAt and updatedAt
});

// Virtual field (not stored in DB)
userSchema.virtual('fullName').get(function() {
  return \`\${this.firstName} \${this.lastName}\`;
});

// Pre-save middleware (hook)
userSchema.pre('save', async function(next) {
  if (this.isModified('password')) {
    this.password = await bcrypt.hash(this.password, 12);
  }
  next();
});

// Instance method
userSchema.methods.greet = function() {
  return \`Hello, I am \${this.name}\`;
};

// Static method
userSchema.statics.findByEmail = function(email) {
  return this.findOne({ email: email.toLowerCase() });
};

const User = mongoose.model('User', userSchema);
`;
console.log(userSchemaCode);

// ─── 2. CRUD Operations ───────────────────────────────────────────────────────
console.log("2) CRUD operation patterns:\n");

const crudCode = `
// CREATE
const user = new User({ name: 'Alice', email: 'alice@example.com' });
await user.save();

// Or shorthand:
const user = await User.create({ name: 'Alice', email: 'alice@example.com' });


// READ
const all = await User.find();                        // all documents
const alice = await User.findById(id);                // by _id
const user = await User.findOne({ email: 'alice@example.com' });

// With query options
const result = await User.find({ role: 'admin' })
  .select('name email -_id')   // fields to include/exclude
  .sort({ createdAt: -1 })     // newest first
  .limit(10)
  .skip(0)                     // pagination offset
  .lean();                     // plain JS object (faster, no Mongoose methods)


// UPDATE
await User.findByIdAndUpdate(id,
  { $set: { role: 'admin' } },
  { new: true, runValidators: true }  // return updated doc + validate
);

// UPDATE OPERATORS
// $set    — set fields
// $unset  — remove fields
// $push   — add to array
// $pull   — remove from array
// $inc    — increment number


// DELETE
await User.findByIdAndDelete(id);
await User.deleteMany({ isActive: false });


// POPULATION (JOIN equivalent)
const post = await Post.findById(id).populate('author', 'name email');


// AGGREGATION
const stats = await User.aggregate([
  { $match: { isActive: true } },
  { $group: { _id: '$role', count: { $sum: 1 } } },
  { $sort: { count: -1 } },
]);
`;
console.log(crudCode);

// ─── 3. Connection setup ─────────────────────────────────────────────────────
console.log("3) Connection setup:\n");
const connectionCode = `
mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
  .then(() => console.log('MongoDB connected'))
  .catch(err => {
    console.error('Connection error:', err.message);
    process.exit(1);
  });

mongoose.connection.on('disconnected', () => console.warn('MongoDB disconnected'));
`;
console.log(connectionCode);

// ─── 4. Simulated in-memory CRUD (runnable) ───────────────────────────────────
console.log("4) In-memory CRUD simulation (runs without MongoDB):\n");

class InMemoryModel {
  constructor(name) {
    this.name = name;
    this.docs = [];
    this._nextId = 1;
  }

  create(data) {
    const doc = { _id: String(this._nextId++), ...data, createdAt: new Date().toISOString() };
    this.docs.push(doc);
    return doc;
  }

  find(query = {}) {
    return this.docs.filter((d) =>
      Object.entries(query).every(([k, v]) => d[k] === v)
    );
  }

  findById(id) { return this.docs.find((d) => d._id === id) || null; }

  findByIdAndUpdate(id, update) {
    const doc = this.findById(id);
    if (!doc) return null;
    Object.assign(doc, update.$set || update);
    return doc;
  }

  findByIdAndDelete(id) {
    const idx = this.docs.findIndex((d) => d._id === id);
    if (idx === -1) return null;
    return this.docs.splice(idx, 1)[0];
  }
}

const UserModel = new InMemoryModel("User");

const alice = UserModel.create({ name: "Alice", email: "alice@example.com", role: "user" });
const bob   = UserModel.create({ name: "Bob",   email: "bob@example.com",   role: "admin" });
console.log("   Created:", alice);
console.log("   Created:", bob);

console.log("   All users:", UserModel.find());
console.log("   Admins only:", UserModel.find({ role: "admin" }));
console.log("   Find by ID:", UserModel.findById(alice._id));

UserModel.findByIdAndUpdate(alice._id, { $set: { role: "moderator" } });
console.log("   After update:", UserModel.findById(alice._id));

UserModel.findByIdAndDelete(bob._id);
console.log("   After delete:", UserModel.find());
