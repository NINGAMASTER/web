document.addEventListener("DOMContentLoaded", function () {
	const chatToggle = document.querySelector(".chat-toggle");
	const chatContainer = document.querySelector(".chat-container");
	const chatClose = document.querySelector(".chat-close");
	const sendBtn = document.querySelector(".send-btn");
	const chatInput = document.querySelector(".chat-input input");
	const chatMessages = document.querySelector(".chat-messages");

	// Переключение видимости чата
	chatToggle.addEventListener("click", function () {
		chatContainer.classList.toggle("active");
		chatToggle.classList.toggle("active");
	});

	// Закрытие чата
	chatClose.addEventListener("click", function () {
		chatContainer.classList.remove("active");
		chatToggle.classList.remove("active");
	});

	// Отправка сообщения
	function sendMessage() {
		const message = chatInput.value.trim();
		if (message) {
			// Добавляем сообщение пользователя
			addMessage(message, "user");
			chatInput.value = "";

			// Отправляем на сервер
			fetch("/process", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ text: message }),
			})
				.then(response => response.json())
				.then(data => {
					// Добавляем ответ бота
					addMessage(data.response, "bot");
				})
				.catch(error => {
					addMessage("Произошла ошибка при подключении к серверу.", "bot");
				});
		}
	}

	// Добавление сообщения в чат
	function addMessage(text, sender) {
		const messageDiv = document.createElement("div");
		messageDiv.classList.add("message", sender + "-message");
		messageDiv.innerHTML = `<p>${text}</p>`;
		chatMessages.appendChild(messageDiv);
		chatMessages.scrollTop = chatMessages.scrollHeight;
	}

	// Обработчики событий
	sendBtn.addEventListener("click", sendMessage);
	chatInput.addEventListener("keypress", function (e) {
		if (e.key === "Enter") {
			sendMessage();
		}
	});
});
