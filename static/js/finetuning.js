const detailsModal = new bootstrap.Modal(document.getElementById("detailFineTuningModal"));
const metricsModal = new bootstrap.Modal(document.getElementById("metricsModal"));

// Tambahkan event listener ke tombol create
async function loadDetails(finetuningId) {
  try {
    const response = await fetch(`/dashboard/train-model/fine-tuning/${finetuningId}`);
    const data = await response.text();
    document.getElementById("modalContent").innerHTML = data;
    detailsModal.show();
  } catch (error) {
    console.error("Error loading details:", error);
    document.getElementById("modalContent").innerHTML =
      /* html */
      `<div class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        Error loading details. Please try again later.
      </div>`;
    detailsModal.show();
  }
}

function showSteps(finetuningId) {
  fetch(`/dashboard/train-model/fine-tuning/show-steps/${finetuningId}`)
    .then((response) => response.text())
    .then((html) => {
      const modalElement = document.getElementById("stepsModal");
      modalElement.querySelector("#stepsContent").innerHTML = html;
      const modal = new bootstrap.Modal(modalElement);
      modal.show();
    })
    .catch((error) => {
      console.error("Error loading metrics:", error);
      alert("Error loading metrics. Please try again.");
    });
}

function loadStepsPage(finetuningId, page) {
  fetch(`/dashboard/train-model/fine-tuning/show-steps/${finetuningId}/${page}`)
    .then((response) => response.text())
    .then((html) => {
      // Replace the modal content with the new HTML
      document.querySelector(".steps-container").innerHTML = html;

      // Reinitialize any charts or other components if needed
      const stepsChart = document.getElementById("stepsChart");
      if (stepsChart) {
        initializeChart(stepsChart);
      }
    })
    .catch((error) => {
      console.error("Error loading metrics page:", error);
    });
}

async function createModel() {
  const form = document.getElementById("createModelForm");
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  try {
    const response = await fetch("/dashboard/train-model/fine-tuning/create-finetuning/jobs", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (result.success) {
      location.reload();
    } else {
      alert("Error creating model: " + result.error);
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Error creating model. Please try again.");
  }
}

async function deleteFinetuning(finetuningId) {
  if (confirm("Are you sure you want to delete this fine-tuning job?")) {
    try {
      const response = await fetch(`/train-finetuning/delete-finetuning/${finetuningId}`, {
        method: "DELETE",
      });

      const result = await response.json();

      if (result.success) {
        location.reload();
      } else {
        alert("Error deleting fine-tuning job: " + result.error);
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Error deleting fine-tuning job. Please try again.");
    }
  }
}

function confirmDelete(jobId) {
  Swal.fire({
    title: "Are you sure?",
    text: "This fine-tuning job will be permanently deleted!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#dc3545",
    cancelButtonColor: "#6c757d",
    confirmButtonText: "Yes, delete it!",
    cancelButtonText: "Cancel",
  }).then((result) => {
    if (result.isConfirmed) {
      // Submit form untuk delete
      fetch(`/train-finetuning/model/${jobId}`, {
        method: "POST",
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            Swal.fire("Deleted!", "Fine-tuning job has been deleted.", "success").then(() => {
              window.location.reload();
            });
          } else {
            Swal.fire("Error!", data.error || "Something went wrong!", "error");
          }
        })
        .catch((error) => {
          Swal.fire("Error!", "Failed to delete fine-tuning job.", "error");
        });
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  // Get the form element
  const form = document.querySelector("#createFinetuningModal form");

  // Add submit event listener
  form.addEventListener("submit", function (event) {
    event.preventDefault();

    // Check if form is valid
    if (form.checkValidity()) {
      // If valid, submit the form
      form.submit();
    }

    form.classList.add("was-validated");
  });

  // Reset form and validation when modal is closed
  const modal = document.getElementById("createFinetuningModal");
  modal.addEventListener("hidden.bs.modal", function () {
    form.reset();
    form.classList.remove("was-validated");
  });
});
