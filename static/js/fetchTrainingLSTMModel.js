import { addLayer } from "./components/add-layer-training-lstm.js";
import { fetchAndDisplayModels } from "./utils/fetchAndDisplayModels.js";
import { trainModel } from "./utils/trainModel.js";

let trainingInProgress = false;

window.addEventListener("beforeunload", function (e) {
  if (trainingInProgress) {
    const confirmationMessage = "Training is in progress. Are you sure you want to leave?";
    e.returnValue = confirmationMessage;
    return confirmationMessage;
  }
});

// Add initial layer on modal open
document.addEventListener("DOMContentLoaded", function () {
  const trainBtn = document.getElementById("train-button");
  const addLayerBtn = document.getElementById("add-layer-btn");

  trainBtn.addEventListener("click", async () => {
    await trainModel();
  });
  addLayerBtn.addEventListener("click", addLayer);
  fetchAndDisplayModels();
});
