import { setFormEnabled } from "./setFormEnable.js";
import { showMessage } from "../components/show-message.js";
import { fetchAndDisplayModels } from "./fetchAndDisplayModels.js";

export const finishTraining = (message, isError = false) => {
  trainingInProgress = false;
  setFormEnabled(true);
  showMessage(message, isError);

  if (!isError) {
    // Reload models table after successful training
    fetchAndDisplayModels();
    // Hide modal after short delay
    setTimeout(() => {
      const modal = document.getElementById("createTrainingModal");
      if (typeof modal.hide === "function") {
        modal.hide();
      }
    }, 2000);
  }
};
