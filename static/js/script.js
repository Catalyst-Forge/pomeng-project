import { handleChat } from "./utils/handleChat.js";
import { CRUDDatasetHandler } from "./utils/crudDatasetHandler.js";
import { generateBreadcrumb } from "./utils/generateBreadcrumb.js";

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
    const breadcrumbLinks = document.querySelectorAll(".breadcrumb-link");

    const toggleSubmenu = (item) => {
      closeAllSubmenus(item); // Tutup semua submenu kecuali yang sedang diklik
      const submenu = item.querySelector(".submenu");
      submenu.classList.toggle("submenu-open");
      submenu.classList.toggle("submenu-closed");
      item.classList.toggle("active");
    };

    const closeAllSubmenus = (excludeItem) => {
      hasSubItems.forEach((el) => {
        if (el !== excludeItem) {
          const submenu = el.querySelector(".submenu");
          if (submenu) {
            submenu.classList.add("submenu-closed");
            submenu.classList.remove("submenu-open");
            el.classList.remove("active");
          }
        }
      });
    };

    const activateLinkBasedOnURL = () => {
      sidebarItems.forEach((item) => {
        const links = item.querySelectorAll(".sidebar-link, .submenu-link");
        links.forEach((link) => {
          if (window.location.href === link.href) {
            item.classList.add("active");
            link.classList.add("active");

            const submenu = item.querySelector(".submenu");
            if (submenu) {
              submenu.classList.replace("submenu-closed", "submenu-open");
            }
          }
        });
      });
    };

    // Event listeners for submenu toggle only if page has sub-items
    if (segments.length >= 2 && segments[1] === "dashboard") {
      hasSubItems.forEach((item) => {
        const submenu = item.querySelector(".submenu");
        if (submenu) {
          submenu.classList.add("submenu-closed");
          item.addEventListener("click", (e) => {
            e.stopPropagation();
            toggleSubmenu(item);
          });
        }
      });

      // Activate links based on URL if dashboard has sub-items
      activateLinkBasedOnURL();
    } else {
      // No sub-items, activate links directly
      sidebarItems.forEach((item) => {
        const link = item.querySelector(".sidebar-link");

        // Aktifkan hanya jika URL cocok secara persis
        if (link && window.location.href === link.href) {
          item.classList.add("active");
          link.classList.add("active");
        }
      });
    }

    // Generate breadcrumb on page load
    generateBreadcrumb(currentPage);

    breadcrumbLinks.forEach((bcLink) => {
      if (bcLink.href.endsWith("/dashboard/dataset/fine-tuning")) {
        bcLink.setAttribute("href", "/dashboard/dataset/fine-tuning/list");
      }

      if (bcLink.href.endsWith("/dashboard/dataset")) {
        bcLink.setAttribute("href", "/dashboard/dataset/list");
      }
    });
  });
}

/**
 *  Function for Dataset Page
 */
if (currentPage === "/dashboard/dataset") {
  const container = document.querySelector("#content");
  CRUDDatasetHandler(container);
}

/**
 *  Function for Fine Tuning Page
 */

if (currentPage === "/dashboard/dataset/fine-tuning/list") {
  document.addEventListener("DOMContentLoaded", () => {
    const deleteForms = document.querySelectorAll(".delete-form");

    deleteForms.forEach((form) => {
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        const dataId = form.dataset.id;

        Swal.fire({
          title: "Apakah Anda yakin ingin menghapus data?",
          text: "Data ini akan dihapus dan tidak bisa dipulihkan!",
          icon: "warning",
          showCancelButton: true,
          confirmButtonColor: "#d33",
          cancelButtonColor: "#3085d6",
          confirmButtonText: "Delete",
        }).then((result) => {
          if (result.isConfirmed) {
            form.action = `/dashboard/dataset/fine-tuning/${dataId}/delete`;
            form.submit();
          }
        });
      });
    });
  });
}
