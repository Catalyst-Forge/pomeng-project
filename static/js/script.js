import { handleChat } from "./utils/handleChat.js";
import { CRUDDatasetHandler } from "./utils/crudDatasetHandler.js";
import { generateBreadcrumb } from "./utils/generateBreadcrumb.js";
import { createSunEditor } from "./utils/createSunEditor.js";

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
  window.addEventListener("load", function () {
    const breadcrumbLinks = document.querySelectorAll(".breadcrumb-link");

    breadcrumbLinks.forEach((bcLink) => {
      if (bcLink.href.endsWith("/dashboard/dataset/fine-tuning")) bcLink.setAttribute("href", "/dashboard/dataset/fine-tuning/list");
      if (bcLink.href.endsWith("/dashboard/dataset")) bcLink.setAttribute("href", "/dashboard/dataset/lstm/list");
      if (bcLink.href.endsWith("/dashboard/train-model/lstm")) bcLink.setAttribute("href", "/dashboard/train-model/lstm/manage/model");
    });
  });

  document.addEventListener("DOMContentLoaded", function () {
    const segments = currentPage.split("/");
    const sidebarItems = document.querySelectorAll(".sidebar-item");
    const hasSubItems = document.querySelectorAll(".sidebar-item.has-sub");

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
          const linkUrl = new URL(link.href, window.location.href).pathname;

          if (linkUrl.includes(`/${segments[2]}/${segments[3]}`) === currentPage.includes(`/${segments[2]}/${segments[3]}`) && segments.length > 2) {
            item.classList.add("active");
            link.classList.add("active");

            const submenu = item.querySelector(".submenu");
            if (submenu) {
              submenu.classList.replace("submenu-closed", "submenu-open");
            }
          } else if (linkUrl === currentPage) {
            item.classList.add("active");
            link.classList.add("active");
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
    }

    // Generate breadcrumb on page load
    generateBreadcrumb(currentPage);
  });
}

/**
 *  Function for LSTM Dataset Page
 */
if (currentPage === "/dashboard/dataset/lstm/list") {
  const container = document.querySelector("#content");
  CRUDDatasetHandler(container);

  // Inisialisasi Tagify untuk input patterns
  const input = document.querySelector("#update-patterns");
  const tagify = new Tagify(input);

  // Event listener untuk menangani tombol modal dan form submit
  document.addEventListener("click", (event) => {
    // Cek jika tombol yang diklik adalah untuk membuka modal
    if (event.target.classList.contains("open-update-modal-button")) {
      // Ambil data patterns dari tombol dan set ke Tagify
      let patterns = event.target.getAttribute("data-patterns"); // Contoh: "web,java,python"
      tagify.loadOriginalValues(); // Reset Tagify
      input.value = patterns; // Set nilai patterns
      tagify.update(); // Update Tagify
    }
  });

  document.querySelector("#updateModal").addEventListener("submit", (event) => {
    // Convert Tagify data ke string dipisahkan koma sebelum submit
    input.value = tagify.value.map((tag) => tag.value).join(", ");
  });
}

/**
 *  Function for Fine-tuning Dataset Page
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

/**
 *  Function for Add Dataset Fine-tuning Page
 */
if (currentPage === "/dashboard/dataset/fine-tuning/add") {
  // Create Textarea Sun Editor
  const systemConversation = document.querySelector("#systemConversation"),
    userConversation = document.querySelector("#userConversation"),
    assistantConversation = document.querySelector("#assistantConversation"),
    systemConversationEditor = createSunEditor(systemConversation),
    userConversationEditor = createSunEditor(userConversation),
    assistantConversationEditor = createSunEditor(assistantConversation);

  document.addEventListener("DOMContentLoaded", () => {
    // Handle for textarea Sun Editor
    document.getElementById("create-form").addEventListener("submit", (e) => {
      const systemConversationEditorContent = systemConversationEditor.getContents(),
        userConversationEditorContent = userConversationEditor.getContents(),
        assistantConversationEditorContent = assistantConversationEditor.getContents();

      systemConversation.value = systemConversationEditorContent;
      userConversation.value = userConversationEditorContent;
      assistantConversation.value = assistantConversationEditorContent;
    });
  });
}

/**
 *  Function for Update Dataset Fine-tuning Page
 */
if (currentPage.includes("/dashboard/dataset/fine-tuning") && currentPage.endsWith("/update")) {
  // Create Textarea Sun Editor
  const systemConversation = document.querySelector("#systemConversation"),
    userConversation = document.querySelector("#userConversation"),
    assistantConversation = document.querySelector("#assistantConversation"),
    systemConversationEditor = createSunEditor(systemConversation),
    userConversationEditor = createSunEditor(userConversation),
    assistantConversationEditor = createSunEditor(assistantConversation);

  document.addEventListener("DOMContentLoaded", () => {
    // Handle for textarea Sun Editor
    document.getElementById("update-form").addEventListener("submit", (e) => {
      const systemConversationEditorContent = systemConversationEditor.getContents(),
        userConversationEditorContent = userConversationEditor.getContents(),
        assistantConversationEditorContent = assistantConversationEditor.getContents();

      systemConversation.value = systemConversationEditorContent;
      userConversation.value = userConversationEditorContent;
      assistantConversation.value = assistantConversationEditorContent;
    });
  });
}
