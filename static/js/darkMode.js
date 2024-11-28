/*!
 * Color mode toggler for Bootstrap's docs (https://getbootstrap.com/)
 * Copyright 2011-2024 The Bootstrap Authors
 * Licensed under the Creative Commons Attribution 3.0 Unported License.
 */

(() => {
  "use strict";

  const getStoredTheme = () => localStorage.getItem("theme");
  const setStoredTheme = (theme) => localStorage.setItem("theme", theme);

  const getPreferredTheme = () => {
    const storedTheme = getStoredTheme();
    if (storedTheme) {
      return storedTheme;
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };

  const applyImmediateTheme = () => {
    const preferredTheme = getPreferredTheme();
    document.documentElement.setAttribute("data-bs-theme", preferredTheme);
  };

  // Apply the theme immediately when the script is loaded
  applyImmediateTheme();

  const setTheme = (theme) => {
    if (theme === "auto") {
      document.documentElement.setAttribute("data-bs-theme", window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    } else {
      document.documentElement.setAttribute("data-bs-theme", theme);
    }
  };

  const initThemeSwitcher = () => {
    const checkbox = document.querySelector('.toggle-switch input[type="checkbox"]');
    const preferredTheme = getPreferredTheme();

    // Set the initial state of the checkbox based on the stored theme
    checkbox.checked = preferredTheme === "dark";

    // Add event listener to toggle theme on checkbox change
    checkbox.addEventListener("change", () => {
      const newTheme = checkbox.checked ? "dark" : "light";
      setStoredTheme(newTheme);
      setTheme(newTheme);
    });

    // Apply the theme
    setTheme(preferredTheme);
  };

  document.addEventListener("DOMContentLoaded", initThemeSwitcher);
})();
