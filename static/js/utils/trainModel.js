import { setFormEnabled } from "./setFormEnable.js";
import { finishTraining } from "./finishTraining.js";

export const trainModel = async () => {
  const form = document.getElementById("model-form");
  const formData = new FormData(form);
  const progressBar = document.getElementById("progress");
  const progressStatus = document.getElementById("progress-status");

  // Show progress and disable form
  document.getElementById("progress-container").classList.remove("d-none");
  setFormEnabled(false);

  const layerConfigs = Array.from(document.querySelectorAll("#layers-container .layer")).map((layerDiv) => ({
    type: layerDiv.querySelector('select[name="layer_type"]').value,
    neurons: parseFloat(layerDiv.querySelector('input[name="neurons_rate"]').value),
  }));

  try {
    const response = await fetch("/dashboard/training-models/training-lstm/train", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        embedding_dim: parseInt(formData.get("embedding_dim")),
        layers: layerConfigs,
        learning_rate: parseFloat(formData.get("learning_rate")),
        batch_size: parseInt(formData.get("batch_size")),
        epochs: parseInt(formData.get("epochs")),
      }),
    });

    const reader = response.body.getReader();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const progressData = new TextDecoder().decode(value).match(/data:(.*)/g);
      progressData?.forEach((match) => {
        try {
          const { progress } = JSON.parse(match.replace("data:", ""));
          progressBar.style.width = `${progress}%`;
          progressStatus.textContent = `${progress}%`;

          if (progress >= 100) finishTraining("Model training completed successfully!");
        } catch (e) {
          console.error("Error parsing progress data:", e);
        }
      });
    }
  } catch (error) {
    console.error("Training error:", error);
    finishTraining("An error occurred during training.", true);
  }
};
