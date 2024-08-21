import { navigateTo } from "./utils/navigate.js";
import { handleChat } from "./utils/handleChat.js";

/**
 *  Queries Elements
 */
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");

/**
 *  API Config
 */
let userMessage = null;
const API_KEY = "API-KEY";
const API_URL_OPENAI = "https://api.openai.com/v1/chat/completions";
const API_URL_DATASET = "/predict";

if (location.pathname === "/chat-bot") {
  const inputInitHeight = chatInput.scrollHeight; // Get input height value

  chatInput.addEventListener("input", () => {
    chatInput.style.height = `${inputInitHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
  });

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
      e.preventDefault();
      handleChat(API_URL_OPENAI, API_KEY, API_URL_DATASET, chatInput, chatbox, inputInitHeight, userMessage);
    }
  });

  sendChatBtn.addEventListener("click", handleChat(API_URL_OPENAI, API_KEY, API_URL_DATASET, chatInput, chatbox, inputInitHeight, userMessage));
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
