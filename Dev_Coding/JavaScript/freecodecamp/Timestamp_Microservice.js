// FreeCodeCamp Back End Development and APIs - Timestamp Microservice
// Parses date strings or Unix timestamps and returns standard JSON payload

function parseDateInput(dateInput) {
  // If no date parameter is supplied, return current date
  if (!dateInput || dateInput.trim() === "") {
    const now = new Date();
    return { unix: now.getTime(), utc: now.toUTCString() };
  }

  let date;

  // Check if dateInput is all digits (Unix timestamp in milliseconds)
  if (/^\d+$/.test(dateInput)) {
    date = new Date(parseInt(dateInput, 10));
  } else {
    date = new Date(dateInput);
  }

  // Validate date
  if (isNaN(date.getTime())) {
    return { error: "Invalid Date" };
  }

  return {
    unix: date.getTime(),
    utc: date.toUTCString()
  };
}

// Tests
console.log("=== Timestamp Microservice Tests ===");
console.log('parseDateInput("2015-12-25") ->', parseDateInput("2015-12-25"));
console.log('parseDateInput("1451001600000") ->', parseDateInput("1451001600000"));
console.log('parseDateInput("") [Current] ->', parseDateInput(""));
console.log('parseDateInput("invalid-date-string") ->', parseDateInput("invalid-date-string"));
