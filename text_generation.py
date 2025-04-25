import g4f.Provider
from g4f.client import Client
from config import INITIAL_HISTORY, MAX_HISTORY_LENGTH
import time

class DialogManager:
    def __init__(self):
        # Инициализация истории диалога
        self.history = INITIAL_HISTORY.copy()  # Начальная история
        self.client = Client()
        self.last_request = time.time()

    def generate_response(self, user_input):
        # Ограничение частоты запросов
        if time.time() - self.last_request < 0.5:
            return "Дайте подумать..."
            
        self.last_request = time.time()
        
        # Добавляем пользовательский ввод в историю
        self.history.append({"role": "user", "content": user_input[:200]})  # Обрезаем длинный ввод
        
        # Обрезаем историю, чтобы она не превышала максимальную длину
        if len(self.history) > MAX_HISTORY_LENGTH * 2:
            # Сохраняем системное сообщение и обрезаем старые сообщения
            self.history = [self.history[0]] + self.history[-MAX_HISTORY_LENGTH:]
        
        try:
            # Генерация ответа с использованием истории
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Модель для генерации claude-3-haiku
                messages=self.history,    # Передаем всю историю
                temperature=0.7,         # Параметр креативности
                max_tokens=1000,          # Ограничение длины ответа
                stream=False             # яПотоковый ответ отключен
            )
            
            # Получаем ответ от ИИ
            ai_response = response.choices[0].message.content.strip()
            
            # Добавляем ответ ИИ в историю
            self.history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            return f"Ошибка: {str(e)}"