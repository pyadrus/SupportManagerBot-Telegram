document.getElementById('login-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const username = this.username.value;
    const password = this.password.value;

    // --- ВРЕМЕННЫЕ ДАННЫЕ ДЛЯ ВХОДА ---
    // В реальном приложении эти данные должны проверяться на сервере
    const operatorCredentials = {
        login: 'operator1',
        pass: 'pass123'
    };

    const adminCredentials = {
        login: 'admin',
        pass: 'adminpass'
    };
    // ------------------------------------

    if (username === operatorCredentials.login && password === operatorCredentials.pass) {
        window.location.href = 'operator.html';
    } else if (username === adminCredentials.login && password === adminCredentials.pass) {
        window.location.href = 'admin.html';
    } else {
        alert('Неверный логин или пароль!');
    }
});