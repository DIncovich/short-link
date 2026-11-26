const API_URL = "";

document.addEventListener("DOMContentLoaded", function() {
    updateUI();
    loadRanking();
});

function showMessage(text, type) {
    if (!type) type = "error";
    const box = document.getElementById("message-box");
    box.textContent = text;
    box.className = "alert " + type;
    box.classList.remove("hidden");
    setTimeout(function() {
        box.classList.add("hidden");
    }, 5000);
}

function switchAuthTab(tab) {
    const loginForm = document.getElementById("login-form");
    const regForm = document.getElementById("register-form");
    const tabLogin = document.getElementById("tab-login");
    const tabReg = document.getElementById("tab-register");

    if (tab === "login") {
        loginForm.classList.remove("hidden");
        regForm.classList.add("hidden");
        tabLogin.classList.add("active");
        tabReg.classList.remove("active");
    } else {
        loginForm.classList.add("hidden");
        regForm.classList.remove("hidden");
        tabLogin.classList.remove("active");
        tabReg.classList.add("active");
    }
}

function updateUI() {
    const token = localStorage.getItem("token");
    const username = localStorage.getItem("username");

    if (token) {
        document.getElementById("auth-section").classList.add("hidden");
        document.getElementById("shortener-section").classList.remove("hidden");
        document.getElementById("user-panel").classList.remove("hidden");
        document.getElementById("username-display").textContent = username;
    } else {
        document.getElementById("auth-section").classList.remove("hidden");
        document.getElementById("shortener-section").classList.add("hidden");
        document.getElementById("user-panel").classList.add("hidden");
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById("reg-username").value;
    const password = document.getElementById("reg-password").value;

    try {
        const response = await fetch(API_URL + "/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: username, password: password })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Ошибка регистрации");

        showMessage("Регистрация успешна! Теперь войдите в аккаунт.", "success");
        switchAuthTab("login");
        document.getElementById("login-username").value = username;
    } catch (err) {
        showMessage(err.message, "error");
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    try {
        const response = await fetch(API_URL + "/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Неверный логин или пароль");

        localStorage.setItem("token", data.access_token);
        localStorage.setItem("username", username);
        updateUI();
        showMessage("Вы успешно вошли!", "success");
    } catch (err) {
        showMessage(err.message, "error");
    }
}

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    document.getElementById("short-result").classList.add("hidden");
    updateUI();
}

async function handleShorten(e) {
    e.preventDefault();
    const url = document.getElementById("original-url").value;
    const ttlInput = document.getElementById("ttl-days").value;
    const token = localStorage.getItem("token");

    const payload = { url: url };
    if (ttlInput) payload.ttl_days = parseInt(ttlInput, 10);

    try {
        const response = await fetch(API_URL + "/shorten", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify(payload)
        });

        if (response.status === 401) {
            logout();
            throw new Error("Сессия истекла. Пожалуйста, войдите снова.");
        }

        const data = await response.json();
        if (!response.ok) {
            const errorMsg = Array.isArray(data.detail) ? data.detail[0].msg : data.detail;
            throw new Error(errorMsg || "Ошибка при сокращении ссылки");
        }

        const linkEl = document.getElementById("short-url-link");
        linkEl.href = data.short_url;
        linkEl.textContent = data.short_url;

        const expiresEl = document.getElementById("expires-info");
        expiresEl.textContent = data.expires_at 
            ? "Действует до: " + new Date(data.expires_at).toLocaleString() 
            : "Бессрочная ссылка";

        document.getElementById("short-result").classList.remove("hidden");
        document.getElementById("original-url").value = "";
        document.getElementById("ttl-days").value = "";
    } catch (err) {
        showMessage(err.message, "error");
    }
}

function copyShortUrl() {
    const url = document.getElementById("short-url-link").textContent;
    navigator.clipboard.writeText(url);
    showMessage("Ссылка скопирована в буфер обмена!", "success");
}

async function loadRanking() {
    const tbody = document.getElementById("ranking-body");
    try {
        const response = await fetch(API_URL + "/ranking/weekly");
        const data = await response.json();

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">Пока нет переходов за последнюю неделю</td></tr>';
            return;
        }

        tbody.innerHTML = data.map(function(item) {
            return '<tr>' +
                '<td class="col-short truncate"><a href="' + item.short_url + '" target="_blank">' + item.short_url + '</a></td>' +
                '<td class="col-orig truncate" title="' + item.original_url + '">' + item.original_url + '</td>' +
                '<td class="col-clicks"><strong>' + item.weekly_clicks + '</strong></td>' +
            '</tr>';
        }).join("");
    } catch (err) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: var(--error);">Не удалось загрузить рейтинг (проверьте, запущен ли бэкенд)</td></tr>';
    }
}
