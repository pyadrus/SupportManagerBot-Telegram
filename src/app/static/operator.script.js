document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const logoutBtn = document.getElementById('logout-btn'); // ИЗМЕНЕНО

    // Модальное окно
    const modal = document.getElementById('requests-modal');
    const requestsIcon = document.getElementById('requests-icon');
    // ИЗМЕНЕНО: Ищем все кнопки "Назад"
    const backButtons = document.querySelectorAll('.back-button');

    // ИЗМЕНЕНО: Логика выхода
    logoutBtn.addEventListener('click', () => {
        window.location.href = 'index.html';
    });

    // Отправка сообщения
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const messageText = messageInput.value.trim();
        if (messageText === '') return;

        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'operator-message');

        const textElement = document.createElement('p');
        textElement.textContent = messageText;

        const timestampElement = document.createElement('span');
        timestampElement.classList.add('timestamp');
        const now = new Date();
        timestampElement.textContent = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}`;

        messageElement.appendChild(textElement);
        messageElement.appendChild(timestampElement);
        chatBox.appendChild(messageElement);

        chatBox.scrollTop = chatBox.scrollHeight;
        messageInput.value = '';
    }

    // Управление модальным окном
    requestsIcon.addEventListener('click', () => {
        modal.style.display = 'block';
    });

    // ИЗМЕНЕНО: Закрытие модальных окон по кнопке "Назад"
    backButtons.forEach(button => {
        button.addEventListener('click', () => {
            button.closest('.modal').style.display = 'none';
        });
    });

    window.addEventListener('click', (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });

    // Обработка принятия заявок
    document.querySelectorAll('.accept-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            alert('Заявка принята! (демо)');
            e.target.closest('.request-item').remove();
            modal.style.display = 'none';
        });
    });
});