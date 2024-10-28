import { handleChat } from "./utils/handleChat.js";
import { CRUDDatasetHandler } from "./utils/crudDatasetHandler.js";

const currentPage = window.location.pathname;

/**
 *  Function for Home Page
 */
if (currentPage === "/") {
  /**
   *  Queries Elements
   */
  const chatbotContainer = document.querySelector(".chatbot");
  const chatbox = document.querySelector(".chatbox");
  const chatInput = document.querySelector(".chat-input textarea");
  const sendChatBtn = document.querySelector(".chat-input span");
  const closeBtn = document.querySelector(".close-btn");
  const openChatBubbleBtn = document.querySelector(".chatbot-bubble-btn");

  /**
   *  API Config
   */
  let userMessage = null;
  const API_KEY = "API-KEY";
  const API_URL_OPENAI = "https://api.openai.com/v1/chat/completions";
  const API_URL_DATASET = "/predict";

  const inputInitHeight = chatInput.scrollHeight; // Get input height value

  // Chat input handler
  chatInput.addEventListener("input", () => {
    chatInput.style.height = `${inputInitHeight}px`;
  });

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
      e.preventDefault();
      handleChat(API_URL_OPENAI, API_KEY, API_URL_DATASET, chatInput, chatbox, inputInitHeight, userMessage);
    }
  });

  // Handle send chat to bot
  sendChatBtn.addEventListener("click", handleChat(API_URL_OPENAI, API_KEY, API_URL_DATASET, chatInput, chatbox, inputInitHeight, userMessage));

  // Handle to close box bot chat
  closeBtn.addEventListener("click", (e) => {
    e.preventDefault();
    chatbotContainer.classList.add("animating-close");

    setTimeout(() => {
      chatbotContainer.classList.remove("animating-close");
      chatbotContainer.classList.add("hidden");
    }, 700);

    setTimeout(() => {
      openChatBubbleBtn.classList.remove("hidden");
    }, 500);
  });

  // Handle to open box bot chat
  openChatBubbleBtn.addEventListener("click", (e) => {
    e.preventDefault();
    chatbotContainer.classList.remove("hidden");
    chatbotContainer.classList.add("animating-open");

    openChatBubbleBtn.classList.add("hidden");

    setTimeout(() => {
      chatbotContainer.classList.remove("animating-open");
    }, 700);
  });
}

/**
 *  Function for Dashboard Page
 */
if (currentPage.startsWith("/dashboard")) {
  document.addEventListener("DOMContentLoaded", function () {
    const segments = currentPage.split("/");
    const sidebarItems = document.querySelectorAll(".sidebar-item");
    const hasSubItems = document.querySelectorAll(".sidebar-item.has-sub");

    // Initiate for nav active in sidebar
    hasSubItems.forEach((item) => {
      const submenu = item.querySelector(".submenu");

      // Hide submenu initially
      submenu.classList.add("submenu-closed");

      // Add event listener for each item with a submenu
      item.addEventListener("click", function (e) {
        e.stopPropagation(); // Prevent event from bubbling up

        // Toggle display for the clicked submenu
        if (submenu.classList.contains("submenu-closed")) {
          // Close other open submenus
          hasSubItems.forEach((el) => {
            const otherSubmenu = el.querySelector(".submenu");
            if (otherSubmenu && otherSubmenu !== submenu) {
              submenu.classList.add("submenu-closed");
            }
          });
          // Open the clicked submenu
          submenu.classList.remove("submenu-closed");
          submenu.classList.add("submenu-open");
        } else {
          // Close the clicked submenu if it's already open
          submenu.classList.remove("submenu-open");
          submenu.classList.add("submenu-closed");
        }
        item.classList.toggle("active");
      });
    });

    // Validate for if one or more segments
    if (segments.length === 2 && segments[1] === "dashboard") {
      sidebarItems.forEach((item) => {
        const sidebarLinks = item.querySelectorAll(".sidebar-link");

        sidebarLinks.forEach((link) => {
          if (window.location.href.includes(link.href)) {
            // If it matches, keep the submenu open and add an active class
            item.classList.add("active");
            link.classList.add("active"); // Highlight the active submenu link
          }
        });
      });
    }

    if (segments.length === 3 && segments[1] === "dashboard") {
      hasSubItems.forEach((item) => {
        const submenu = item.querySelector(".submenu");
        const submenuLinks = submenu.querySelectorAll(".submenu-link");

        // Check if the current URL matches any submenu link
        submenuLinks.forEach((link) => {
          if (window.location.href.includes(link.href)) {
            // If it matches, keep the submenu open and add an active class
            item.classList.add("active");
            link.classList.add("active"); // Highlight the active submenu link
            submenu.classList.remove("submenu-closed");
            submenu.classList.add("submenu-open");
          }
        });
      });
    }
  });
}

/**
 *  Function for Dataset Page
 */
if (currentPage === "/dashboard/dataset") {
  const container = document.querySelector("#content");
  CRUDDatasetHandler(container);
}
