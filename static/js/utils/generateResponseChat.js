export const generateResponse = (userMessage, API_URL, API_KEY, chatbox) => {
  const messageElement = userMessage.querySelector("p");

  const requestOptions = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${API_KEY}`,
    },
    body: JSON.stringify({
      model: "gpt-3.5-turbo",
      messages: [{ role: "user", content: userMessage }],
      temperature: 1,
      max_tokens: 256,
      top_p: 1,
      frequency_penalty: 0,
      presence_penalty: 0,
    }),
  };

  fetch(API_URL, requestOptions)
    .then((res) => res.json())
    .then((data) => {
      console.log(data); // Untuk melihat respons dari API
      if (data.error && data.error.message) {
        messageElement.classList.add("error");
        messageElement.textContent = `Error: ${data.error.message}`;
      } else if (data.choices && data.choices.length > 0) {
        messageElement.textContent = data.choices[0].message.content.trim();
      } else {
        messageElement.classList.add("error");
        messageElement.textContent = "Oops! Something went wrong. Please try again.";
      }
    })
    .catch((error) => {
      console.error(error);
      messageElement.classList.add("error");
      messageElement.textContent = "Oops! Something went wrong. Please try again.";
    })
    .finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
};
