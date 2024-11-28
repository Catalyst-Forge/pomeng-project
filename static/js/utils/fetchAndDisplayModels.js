import { formatDate } from "./formatDate.js";
import { showAlert } from "../components/show-alert.js";
import { displayTrainingHistory } from "../components/training-history-display.js";

// Function to view model details
async function viewModelDetails(version) {
  try {
    const response = await fetch(`/dashboard/training-models/training-lstm/version-history/${version}`);
    const data = await response.json();

    if (response.ok) {
      displayTrainingHistory(data); // Display the training history
    } else {
      throw new Error(data.error || "Failed to fetch model details");
    }
  } catch (error) {
    showAlert(error.message, "error");
  }
}

// Function to restore model
async function restoreModel(version) {
  try {
    const response = await fetch(`/models/${version}/activate`, {
      method: "POST",
    });
    const data = await response.json();

    if (response.ok) {
      showAlert("Model restored successfully", "success");
      await fetchAndDisplayModels();
    } else {
      throw new Error(data.error || "Failed to restore model");
    }
  } catch (error) {
    showAlert(error.message, "error");
  }
}

// Function to delete model
async function deleteModel(version) {
  if (!confirm("Are you sure you want to delete this model?")) {
    return;
  }

  try {
    const response = await fetch(`/models/${version}`, {
      method: "DELETE",
    });
    const data = await response.json();

    if (response.ok) {
      showAlert("Model deleted successfully", "success");
      await fetchAndDisplayModels();
    } else {
      throw new Error(data.error || "Failed to delete model");
    }
  } catch (error) {
    showAlert(error.message, "error");
  }
}

// Function to fetch and display models
export const fetchAndDisplayModels = async () => {
  try {
    const response = await fetch("/models");
    const data = await response.json();
    const tableBody = document.getElementById("models-table-body");
    tableBody.innerHTML = "";

    // Combine active model and other models
    const allModels = [...data.models];
    if (data.active_model) {
      allModels.unshift({
        version: "Current",
        backup_date: data.active_model.training_date,
        status: "active",
        training_metrics: data.active_model.metrics,
      });
    }

    allModels.forEach((model) => {
      const accuracy = model.training_metrics?.final_accuracy ? (model.training_metrics.final_accuracy * 100).toFixed(2) + "%" : "N/A";

      const row = document.createElement("tr");
      row.innerHTML =
        /* html */
        `<td class="align-middle">${model.version}</td>
        <td class="text-center align-middle">${formatDate(model.backup_date)}</td>
        <td class="text-center align-middle">
          <span class="model-status ${model.status === "active" ? "status-active" : "status-inactive"}">
            ${model.status === "active" ? "Active" : "Inactive"}
          </span>
        </td>
        <td class="text-center align-middle">${accuracy}</td>
        <td class="d-flex justify-content-center gap-2"></td>`;
      tableBody.appendChild(row);

      if (model.status === "active") row.lastElementChild.innerHTML = "&ThinSpace;";

      // Add buttons and event listeners
      if (model.status !== "active") {
        const actionsCell = row.lastElementChild;

        // View Details button
        const viewButton = document.createElement("button");
        viewButton.textContent = "View Details";
        viewButton.className = "btn btn-primary btn-sm";
        viewButton.dataset.bsToggle = "modal";
        viewButton.dataset.bsTarget = "#training-model";
        viewButton.addEventListener("click", () => viewModelDetails(model.version));
        actionsCell.appendChild(viewButton);

        // Restore button
        const restoreButton = document.createElement("button");
        restoreButton.textContent = "Restore";
        restoreButton.className = "btn btn-warning btn-sm";
        restoreButton.addEventListener("click", () => restoreModel(model.version));
        actionsCell.appendChild(restoreButton);

        // Delete button
        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";
        deleteButton.className = "btn btn-danger btn-sm";
        deleteButton.addEventListener("click", () => deleteModel(model.version));
        actionsCell.appendChild(deleteButton);
      }
    });
  } catch (error) {
    showAlert("Failed to fetch models", "error");
  }
};
