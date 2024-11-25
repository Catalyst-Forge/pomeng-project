export const generateResponse = (incomingChatLi, API_URL_OPENAI, API_KEY, API_URL_DATASET, chatbox, userMessage) => {
    const messageElement = incomingChatLi.querySelector("p");

    // Request Option dari model sendiri
    const modelData = {
        method: "POST",
        body: JSON.stringify({ message: userMessage }),
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
        },
    };

    // Pertama, coba mendapatkan respons dari model sendiri
    fetch(API_URL_DATASET, modelData)
        .then((res) => res.json())
        .then((data) => {
            if (data) {
                // Jika model sendiri memberikan respons yang valid
                messageElement.textContent = data.answer;
            } else {
                console.log("Data Lili tidak merespon");
            }
        })
        .catch((error) => {
            console.error("Model sendiri error:", error);
            // Jika terjadi kesalahan pada model sendiri, coba API OpenAI
            return fetchOpenAI(userMessage, API_URL_OPENAI, API_KEY, messageElement);
        })
        .finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
};
