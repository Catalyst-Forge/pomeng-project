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

                // Jika model sendiri gagal atau tidak ada respons, coba API OpenAI
                return fetchOpenAI(userMessage, API_URL_OPENAI, API_KEY, messageElement);
            }
        })
        .catch((error) => {
            console.error("Model sendiri error:", error);
            // Jika terjadi kesalahan pada model sendiri, coba API OpenAI
            return fetchOpenAI(userMessage, API_URL_OPENAI, API_KEY, messageElement);
        })
        .finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
};

const fetchOpenAI = async (userMessage, API_URL_OPENAI, API_KEY, messageElement) => {
    // Request Option dari model API OpenAI
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

    try {
        const res = await fetch(API_URL_OPENAI, requestOptions);
        const data = await res.json();
        if (data.error && data.error.message) {
            messageElement.classList.add("error");
            messageElement.textContent = `Error: ${data.error.message}`;
        } else if (data.choices && data.choices.length > 0) {
            messageElement.textContent = data.choices[0].message.content.trim();
        } else {
            messageElement.classList.add("error");
            messageElement.textContent = "Oops! Something went wrong. Please try again.";
        }
    } catch (error) {
        console.error("OpenAI API error:", error);
        messageElement.classList.add("error");
        messageElement.textContent = "Oops! Something went wrong. Please try again.";
    }
};
