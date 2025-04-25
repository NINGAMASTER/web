document.addEventListener("DOMContentLoaded", function () {
	const newsContainer = document.getElementById("news-container");
	// if (!newsContainer) return;

	// Показываем заглушку на время загрузки
	newsContainer.innerHTML = `
        <div class="news-item">
            <img src="/static/assets/img/news-placeholder.webp" alt="Загрузка новостей">
            <h3>Загружаем новости...</h3>
        </div>
    `;

	fetch("/get_news")
		.then(response => {
			if (!response.ok) throw new Error("Network response was not ok");
			return response.json();
		})
		.then(data => {
			if (data.status === "success" && data.news && data.news.length > 0) {
				newsContainer.innerHTML = "";

				data.news.forEach(newsItem => {
					const newsElement = document.createElement("div");
					newsElement.className = "news-item";
					newsElement.innerHTML = `
                        <a href="${newsItem.link || "#"}" target="_blank">
                            <img src="${
															newsItem.image_url ||
															"/static/assets/img/news-placeholder.webp"
														}" 
                                 alt="${newsItem.title || "Новость"}"
                                 onerror="this.src='/static/assets/img/news-placeholder.webp'">
                            <h3>${newsItem.title || "Новость"}</h3>
                            <p>${
															newsItem.description
																? newsItem.description.substring(0, 100) + "..."
																: "Новость из Telegram-канала EcoSurgut"
														}</p>
                        </a>
                    `;
					newsContainer.appendChild(newsElement);
				});
			} else {
				throw new Error("No news data received");
			}
		})
		.catch(error => {
			console.error("Error loading news:", error);
			newsContainer.innerHTML = `
                <div class="news-item">
                    <img src="/static/assets/img/news-placeholder.webp" alt="Ошибка загрузки">
                    <h3>Новости не загрузились</h3>
                    <p>Попробуйте обновить страницу позже</p>
                </div>
            `;
		});
});
