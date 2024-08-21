export const navigateTo = (url, app) => {
  fetch(url)
    .then((response) => response.text())
    .then((html) => {
      app.innerHTML = html;
      history.pushState(null, null, url);
    })
    .catch((error) => console.error("Error fetching page: ", error));
};
