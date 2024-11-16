export const showMessage = (message, isError = false) => {
  const messageElement = document.getElementById("response-message");
  messageElement.textContent = message;
  messageElement.classList.remove("hidden", "bg-green-100", "text-green-800", "bg-red-100", "text-red-800");
  messageElement.classList.add(isError ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800");
};
