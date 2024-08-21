import { createChatLi } from "./createChat.js";
import { generateResponse } from "./generateResponseChat.js";

export const handleChat = (API_URL_OPENAI, API_KEY, API_URL_DATASET, chatInput, chatbox, inputInitHeight, userMessage) => {
  userMessage = chatInput.value.trim();
  if (!userMessage) return;

  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px`;

  chatbox.appendChild(createChatLi(userMessage, "outgoing"));
  chatbox.scrollTo(0, chatbox.scrollHeight);

  setTimeout(() => {
    const incomingChatLi = createChatLi("Thinking...", "incoming");
    chatbox.appendChild(incomingChatLi);
    chatbox.scrollTo(0, chatbox.scrollHeight);
    generateResponse(incomingChatLi, API_URL_OPENAI, API_KEY, API_URL_DATASET, chatbox, userMessage);
  }, 600);
};
