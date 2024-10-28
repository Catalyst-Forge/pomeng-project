export const CRUDDatasetHandler = (container) => {
  // Remove pattern button function
  const removePatternBtn = (button) => button.parentElement.remove();

  // Function for update modal input & action
  let openUpdateModal = (id, tag, patterns, responses) => {
    document.querySelector("#intent-id").value = id;
    document.querySelector("#update-tag").value = tag;
    document.querySelector("#update-patterns").value = patterns; // You can add logic to show patterns better
    document.querySelector("#update-responses").value = responses;
    document.querySelector("#update-form").action = `/dashboard/dataset/${id}/update`; // Set correct action URL
  };

  document.addEventListener("DOMContentLoaded", function () {
    const addPatternBtn = container.querySelector("#add-create-pattern"),
      createForm = container.querySelector("#create-form"),
      updateForm = container.querySelector("#update-form"),
      deleteForm = document.querySelectorAll("#delete-form"),
      openUpdateModalBtn = container.querySelectorAll(".open-update-modal-button");

    // Handle add pattern button in create modal
    addPatternBtn.addEventListener("click", function () {
      const containerPattern = container.querySelector("#create-patterns-list");
      const div = document.createElement("div");
      const input = document.createElement("input");
      const removeBtn = document.createElement("button");

      div.classList.add("pattern-input");
      div.classList.add("input-group");
      div.classList.add("mb-2");

      input.type = "text";
      input.classList.add("form-control");
      input.name = "patterns[]";
      input.placeholder = "Enter pattern";
      input.required = true;

      removeBtn.type = "button";
      removeBtn.classList.add("remove-pattern");
      removeBtn.classList.add("btn");
      removeBtn.classList.add("btn-primary");
      removeBtn.textContent = "Remove";

      removeBtn.addEventListener("click", function () {
        removePatternBtn(removeBtn);
      });

      div.appendChild(input);
      div.appendChild(removeBtn);
      containerPattern.appendChild(div);
    });

    // Handle submit for create intent
    createForm.addEventListener("click", function () {
      const inputs = document.querySelectorAll('#create-patterns-list input[name="patterns[]"]');
      const patterns = Array.from(inputs)
        .map((input) => input.value)
        .filter((pattern) => pattern.trim() !== "") // Filter out empty patterns
        .join(","); // Join patterns with a comma

      console.log("Collected Patterns:", patterns); // Debugging line

      document.querySelector("#create-patterns-hidden").value = patterns; // Set hidden input value
    });

    // Open update modal with existing data
    openUpdateModalBtn.forEach((button) => {
      button.addEventListener("click", () => {
        const datasetId = button.getAttribute("data-id"),
          datasetTag = button.getAttribute("data-tag"),
          datasetPatterns = button.getAttribute("data-patterns"),
          datasetResponses = button.getAttribute("data-responses");

        openUpdateModal(datasetId, datasetTag, datasetPatterns, datasetResponses);
      });
    });

    // Handle submit for update form
    updateForm.addEventListener("submit", function (event) {
      event.preventDefault(); // Prevent default submission
      updateForm.submit();
    });

    // Tambahkan event listener ke tombol `remove-pattern` yang sudah ada (jika ada)
    const removeButtons = container.querySelectorAll(".remove-pattern");
    removeButtons.forEach((button) => button.addEventListener("click", () => removePatternBtn(button)));

    // Handle delete for dataset
    deleteForm.forEach((button) => {
      button.addEventListener("click", () => {
        const datasetId = document.getElementById("dataset-id");
        let dataId = datasetId.getAttribute("data-id");

        deleteForm.forEach((remove) => (remove.action = `/dashboard/dataset/${dataId}/delete`));
      });
    });
  });
};
