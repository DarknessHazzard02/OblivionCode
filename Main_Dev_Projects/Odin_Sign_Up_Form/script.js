// Made by: Hazzard
// Odin Sign-up Form - marks fields as touched (so errors show only after the user
// leaves a field) and checks that both passwords match before the local-only submit.

const form = document.getElementById("signup");
const password = document.getElementById("password");
const confirmPassword = document.getElementById("password_confirm");
const message = document.getElementById("message");

form.querySelectorAll("input").forEach((input) => {
  input.addEventListener("blur", () => input.classList.add("touched"));
});

function checkPasswords() {
  const mismatch = confirmPassword.value !== "" && password.value !== confirmPassword.value;
  confirmPassword.setCustomValidity(mismatch ? "Passwords do not match." : "");
  return !mismatch;
}

password.addEventListener("input", checkPasswords);
confirmPassword.addEventListener("input", checkPasswords);

form.addEventListener("submit", (event) => {
  event.preventDefault();
  form.querySelectorAll("input").forEach((input) => input.classList.add("touched"));
  checkPasswords();
  if (!form.checkValidity()) {
    const firstInvalid = form.querySelector("input:invalid");
    message.className = "message";
    message.textContent = `${firstInvalid.name.replace(/_/g, " ")}: ${firstInvalid.validationMessage}`;
    firstInvalid.focus();
    return;
  }
  message.className = "message ok";
  message.textContent = "All fields are valid. Practice form: nothing was sent.";
});
