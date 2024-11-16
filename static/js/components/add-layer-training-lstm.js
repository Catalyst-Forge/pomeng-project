export const addLayer = () => {
  const layersContainer = document.getElementById("layers-container");
  const layerDiv = document.createElement("div");
  layerDiv.classList.add("col-auto");

  layerDiv.innerHTML =
    /* html */
    `<div>
      <label class="form-label">Layer Type:</label>
      <select name="layer_type" class="form-select">
        <option value="Dense">Dense</option>
        <option value="LSTM">LSTM</option>
        <option value="Dropout">Dropout</option>
      </select>
    </div>
  
    <div>
      <label class="form-label">Neurons/Rate:</label>
      <input type="number" name="neurons_rate" class="form-control" step="0.1" placeholder="0,1" required>
    </div>`;

  layersContainer.appendChild(layerDiv);
};
