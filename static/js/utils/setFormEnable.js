export const setFormEnabled = (enabled) => {
  const form = document.getElementById("model-form");
  const trainButton = document.getElementById("train-button");
  const elements = form.elements;

  for (let element of elements) element.disabled = !enabled;
  trainButton.disabled = !enabled;
};
