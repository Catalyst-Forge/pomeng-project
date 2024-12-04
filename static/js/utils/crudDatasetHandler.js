export const CRUDDatasetHandler = (container) => {
  // Function for remove pattern button
  const removePattern = (button) => button.closest(".pattern-input").remove();

  // Function to handle the pattern input dynamically
  const addPattern = (containerPattern) => {
    const div = document.createElement("div");
    div.classList.add("pattern-input", "input-group", "mb-2");

    const input = document.createElement("input");
    input.type = "text";
    input.classList.add("form-control");
    input.name = "patterns[]";
    input.placeholder = "Enter pattern";
    input.required = true;

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.classList.add("remove-pattern", "btn", "btn-danger");
    removeBtn.textContent = "Remove";
    removeBtn.addEventListener("click", () => removePattern(removeBtn));

    div.append(input, removeBtn);
    containerPattern.appendChild(div);
  };

  // Function to handle update modal
  const openUpdateModal = (id, tag, patterns, responses) => {
    document.querySelector("#intent-id").value = id;
    document.querySelector("#update-tag").value = tag;
    document.querySelector("#update-patterns").value = patterns;
    document.querySelector("#update-responses").value = responses;
    document.querySelector("#update-form").action = `/dashboard/dataset/${id}/update`;
  };

  // Main event listener
  document.addEventListener("DOMContentLoaded", () => {
    const addPatternBtn = container.querySelector("#add-create-pattern"),
      removePatternButtons = container.querySelectorAll(".remove-pattern"),
      createForm = container.querySelector("#create-form"),
      deleteForms = container.querySelectorAll("#delete-form"),
      openUpdateModalBtns = container.querySelectorAll(".open-update-modal-button");

    // Handle add pattern button
    addPatternBtn.addEventListener("click", () => addPattern(container.querySelector("#create-patterns-list")));

    removePatternButtons.forEach((button) => button.addEventListener("click", () => removePattern(button)));

    // Handle submit for create intent
    createForm.addEventListener("click", () => {
      const patterns = Array.from(document.querySelectorAll('#create-patterns-list input[name="patterns[]"]'))
        .map((input) => input.value.trim())
        .filter((pattern) => pattern !== "")
        .join(",");
      document.querySelector("#create-patterns-hidden").value = patterns;
    });

    // Open update modal with existing data
    openUpdateModalBtns.forEach((button) => {
      button.addEventListener("click", () => {
        const { id, tag, patterns, responses } = button.dataset;
        openUpdateModal(id, tag, patterns, responses);
      });
    });

    // Handle delete for dataset
    deleteForms.forEach((form) => {
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        const datasetId = form.dataset.id;

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
            form.action = `/dashboard/dataset/${datasetId}/delete`;
            form.submit();
          }
        });
      });
    });
  });
};
