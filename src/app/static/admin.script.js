document.addEventListener('DOMContentLoaded', () => {
    // --- ДАННЫЕ (ВРЕМЕННОЕ РЕШЕНИЕ С ДЕМО-СТАТИСТИКОЙ) ---
    let operators = [
        {login: 'operator1', pass: 'pass123', stats: {accepted: 142, completed: 130, rating: 4.8}},
        {login: 'operator2', pass: 'pass456', stats: {accepted: 98, completed: 95, rating: 4.6}}
    ];
    //------------------------------------

    const logoutBtn = document.getElementById('logout-btn');
    logoutBtn.addEventListener('click', () => {
        window.location.href = 'index.html';
    });

    // Обновление даты и времени
    const datetimeElement = document.getElementById('current-datetime');

    function updateDateTime() {
        const now = new Date();
        datetimeElement.textContent = now.toLocaleString('ru-RU', {dateStyle: 'long', timeStyle: 'short'});
    }

    updateDateTime();
    setInterval(updateDateTime, 60000);

    // Модальные окна
    const addModal = document.getElementById('add-operator-modal');
    const listModal = document.getElementById('operators-list-modal');
    const personalStatsModal = document.getElementById('personal-stats-modal');
    const allModals = document.querySelectorAll('.modal');

    const addBtn = document.getElementById('add-operator-btn');
    // ИСПРАВЛЕНО: Используем правильный ID кнопки
    const showStatsBtn = document.getElementById('show-stats-btn');

    // Открытие модальных окон
    addBtn.onclick = () => addModal.style.display = 'block';
    // ИСПРАВЛЕНО: Обработчик назначен на правильную переменную
    showStatsBtn.onclick = () => {
        renderOperatorsList();
        listModal.style.display = 'block';
    }

    // Закрытие модальных окон
    allModals.forEach(modal => {
        // По кнопке "Назад"
        modal.querySelector('.back-button').addEventListener('click', () => {
            modal.style.display = 'none';
        });
        // По клику на фон
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });

    // Логика добавления оператора
    document.getElementById('add-operator-form').addEventListener('submit', function (e) {
        e.preventDefault();
        const login = document.getElementById('new-op-login').value;
        const pass = document.getElementById('new-op-pass').value;

        if (operators.find(op => op.login === login)) {
            alert('Оператор с таким логином уже существует!');
            return;
        }

        operators.push({login, pass, stats: {accepted: 0, completed: 0, rating: 'n/a'}});
        alert(`Оператор ${login} успешно добавлен!`);
        this.reset();
        addModal.style.display = 'none';
    });

    // Рендер списка операторов и логика кнопок
    function renderOperatorsList() {
        const list = document.getElementById('operators-list');
        list.innerHTML = '';

        operators.forEach((op, index) => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <span>${op.login}</span>
                <div class="operator-actions">
                    <button class="view-stats-btn" data-login="${op.login}">Статистика</button>
                    <button class="delete-op-btn" data-index="${index}">Удалить</button>
                </div>
            `;
            list.appendChild(listItem);
        });
    }

    // Обработка кликов по списку операторов (делегирование событий)
    document.getElementById('operators-list').addEventListener('click', function (e) {
        const target = e.target;

        // Клик по кнопке "Удалить"
        if (target.classList.contains('delete-op-btn')) {
            const indexToDelete = parseInt(target.getAttribute('data-index'), 10);
            const operatorLogin = operators[indexToDelete].login;
            if (confirm(`Вы уверены, что хотите удалить оператора ${operatorLogin}?`)) {
                operators.splice(indexToDelete, 1);
                renderOperatorsList();
            }
        }

        // Клик по кнопке "Статистика"
        if (target.classList.contains('view-stats-btn')) {
            const operatorLogin = target.getAttribute('data-login');
            const operatorData = operators.find(op => op.login === operatorLogin);
            if (operatorData) {
                showPersonalStats(operatorData);
            }
        }
    });

    // Функция для показа персональной статистики
    function showPersonalStats(operator) {
        document.getElementById('personal-stats-title').textContent = `Статистика: ${operator.login}`;
        document.getElementById('personal-accepted').textContent = operator.stats.accepted;
        document.getElementById('personal-completed').textContent = operator.stats.completed;
        document.getElementById('personal-rating').textContent = operator.stats.rating + ' ⭐️';

        personalStatsModal.style.display = 'block';
    }
});