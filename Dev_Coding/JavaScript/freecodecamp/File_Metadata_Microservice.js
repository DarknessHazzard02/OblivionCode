/**
 * File Metadata Microservice - freeCodeCamp Back End APIs Project
 *
 * Concepts: Multipart form-data, file upload handling, MIME types,
 *           Express + Multer, returning file metadata as JSON
 *
 * Endpoint:
 *   POST /api/fileanalyse  → returns { name, type, size }
 *
 * In a real freeCodeCamp solution this uses Express + Multer.
 * This file is a standalone simulation using the Node.js `fs` module.
 */

const fs = require("fs");
const path = require("path");

// ─── MIME type lookup (simplified) ────────────────────────────────────────────
const MIME_TYPES = {
  ".txt":  "text/plain",
  ".html": "text/html",
  ".css":  "text/css",
  ".js":   "application/javascript",
  ".json": "application/json",
  ".png":  "image/png",
  ".jpg":  "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif":  "image/gif",
  ".svg":  "image/svg+xml",
  ".pdf":  "application/pdf",
  ".zip":  "application/zip",
  ".mp4":  "video/mp4",
  ".mp3":  "audio/mpeg",
};

// ─── Core function ────────────────────────────────────────────────────────────
/**
 * Analyses a file and returns its metadata.
 * @param {string} filePath - Absolute path to the file
 * @returns {{ name: string, type: string, size: number } | { error: string }}
 */
function analyseFile(filePath) {
  if (!fs.existsSync(filePath)) {
    return { error: `File not found: ${filePath}` };
  }

  const stats = fs.statSync(filePath);
  const ext = path.extname(filePath).toLowerCase();
  const name = path.basename(filePath);
  const type = MIME_TYPES[ext] || "application/octet-stream";
  const size = stats.size; // bytes

  return { name, type, size };
}

/**
 * Formats file size as a human-readable string.
 */
function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

// ─── Demo ─────────────────────────────────────────────────────────────────────
console.log("=== File Metadata Microservice Demo ===\n");

// Analyse the current script file itself
const thisFile = __filename;
const result = analyseFile(thisFile);
console.log("1) Analysing this script file:");
if (result.error) {
  console.log("   Error:", result.error);
} else {
  console.log(`   name : ${result.name}`);
  console.log(`   type : ${result.type}`);
  console.log(`   size : ${result.size} bytes (${formatSize(result.size)})`);
}

// Test with a non-existent file
console.log("\n2) Non-existent file:");
console.log("  ", analyseFile("/tmp/ghost.pdf"));

// Simulate multipart endpoint response format
console.log("\n3) Simulated POST /api/fileanalyse response:");
const mockUpload = { originalname: "photo.jpg", mimetype: "image/jpeg", size: 204800 };
console.log("   Input  :", mockUpload);
console.log("   Output :", {
  name: mockUpload.originalname,
  type: mockUpload.mimetype,
  size: mockUpload.size,
});

// MIME type table
console.log("\n4) Supported MIME types:");
Object.entries(MIME_TYPES).forEach(([ext, mime]) => {
  console.log(`   ${ext.padEnd(6)} → ${mime}`);
});
