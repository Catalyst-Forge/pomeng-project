import { navigateTo } from "./utils/navigate.js";
import { handleChat } from "./utils/handleChat.js";

/**
 *  Queries Elements
 */
const app = document.getElementById("app");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");
// const containerText = document.querySelector(".container p");

/**
 *  API Config
 */
let userMessage = null;
const API_KEY = "API-KEY";
const API_URL = "https://api.openai.com/v1/chat/completions";

if (location.pathname === "/chat-bot") {
  const inputInitHeight = chatInput.scrollHeight; // Get input height value

  chatInput.addEventListener("input", () => {
    chatInput.style.height = `${inputInitHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
  });

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
      e.preventDefault();
      handleChat(userMessage, API_URL, API_KEY, chatInput, chatbox, inputInitHeight);
    }
  });

  sendChatBtn.addEventListener("click", handleChat(userMessage, API_URL, API_KEY, chatInput, chatbox, inputInitHeight));
}

// document.addEventListener("DOMContentLoaded", () => {
//   // typeWriterEffect();

//   document.body.addEventListener("click", (e) => {
//     if (e.target.matches("[data-link]")) {
//       e.preventDefault();
//       navigateTo(e.target.href, app);
//     }
//   });

//   const path = location.pathname;
//   if (path === "/") {
//     navigateTo("index.html");
//   } else if (path === "/chat-bot") {
//     navigateTo("chatbot.html");
//   }
// });

// window.addEventListener("popstate", () => {
//   const path = location.pathname;
//   if (path === "/") {
//     navigateTo("index.html");
//   } else if (path === "/chat-bot") {
//     navigateTo("chatbot.html");
//   }
// });
