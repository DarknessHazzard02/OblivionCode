// Made by: Hazzard
// FreeCodeCamp Back End Development and APIs - Request Header Parser Microservice
// Extracts client IP address, preferred language, and system software user-agent from headers

function parseRequestHeaders(headers, remoteAddress = "127.0.0.1") {
  // Extract client IP (handling standard proxies such as x-forwarded-for)
  const ipaddress = headers["x-forwarded-for"]
    ? headers["x-forwarded-for"].split(",")[0].trim()
    : remoteAddress;

  // Extract accept-language
  const language = headers["accept-language"] || "en-US,en;q=0.5";

  // Extract user-agent / software
  const software = headers["user-agent"] || "Mozilla/5.0";

  return {
    ipaddress,
    language,
    software
  };
}

// Simulated Request
const mockHeaders = {
  "host": "localhost:3000",
  "x-forwarded-for": "159.20.14.100, 10.0.0.1",
  "accept-language": "en-US,en;q=0.9,es;q=0.8",
  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
};

console.log("=== Request Header Parser Result ===");
console.log(parseRequestHeaders(mockHeaders));
