import { createChatLi } from "./createChat.js";
import { generateResponse } from "./generateResponseChat.js";

export const handleChat = (userMessage, API_URL, API_KEY, chatInput, chatbox, inputInitHeight) => {
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
    generateResponse(incomingChatLi, API_URL, API_KEY, chatbox);
  }, 600);
};
