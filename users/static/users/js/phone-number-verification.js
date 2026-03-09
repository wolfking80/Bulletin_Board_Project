import { initializeApp } from "https://www.gstatic.com/firebasejs/12.5.0/firebase-app.js";
import {
    getAuth,
    signInWithPhoneNumber,
    RecaptchaVerifier
} from "https://www.gstatic.com/firebasejs/12.5.0/firebase-auth.js";

import { postAction } from "../../../../static/js/utils.js";

// Инициализация приложения Firebase
const app = initializeApp({
    apiKey: window.FIREBASE_API_KEY,
});

// Получаем сервис аутентификации
const auth = getAuth(app);

// Отправка кода подтверждения
const sendCodeBtn = document.getElementById('sendCodeBtn');
sendCodeBtn.addEventListener('click', async () => {
    const spinner = document.getElementById('sendCodeSpinner');
    const errorDiv = document.getElementById('sendCodeError');

    sendCodeBtn.classList.add('d-none');
    spinner.classList.remove('d-none');
    errorDiv.classList.add('d-none');

    try {
        const appVerifier = new RecaptchaVerifier(auth, 'sendCodeBtn', {
            'size': 'invisible'
        });

        window.verificationSession = await signInWithPhoneNumber(
            auth,
            window.USER_PHONE_NUMBER,
            appVerifier
        );

        // SMS отправлено
        // Переходим к шагу ввода кода
        document.getElementById('verificationStep1').classList.add('d-none');
        document.getElementById('verificationStep2').classList.remove('d-none');

        spinner.classList.add('d-none');
    } catch (error) {
        // Ошибка отправки SMS
        spinner.classList.add('d-none');
        sendCodeBtn.classList.remove('d-none');
        errorDiv.textContent = 'Ошибка отправки SMS: ' + error.message;
        errorDiv.classList.remove('d-none');
    }
});

// Проверка кода подтверждения
const verifyCodeForm = document.getElementById('verifyCodeForm');
verifyCodeForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const code = document.getElementById('verificationCodeInput').value;
    const spinner = document.getElementById('verifyCodeSpinner');
    const errorDiv = document.getElementById('verifyCodeError');
    const submitBtn = verifyCodeForm.querySelector('button[type="submit"]');

    submitBtn.classList.add('d-none');
    spinner.classList.remove('d-none');
    errorDiv.classList.add('d-none');

    try {
        // Проверяем код через Firebase Auth
        await window.verificationSession.confirm(code);

        const data = await postAction(window.MARK_PHONE_NUMBER_AS_VERIFIED_URL);

        spinner.classList.add('d-none');

        if (data.success) {
            // Показываем сообщение об успехе
            document.getElementById('verificationStep2').classList.add('d-none');
            document.getElementById('verificationSuccess').classList.remove('d-none');

            // Обновляем страницу через 2 секунды
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            // Показываем ошибку
            submitBtn.classList.remove('d-none');
            errorDiv.textContent = 'Ошибка обновления статуса верификации';
            errorDiv.classList.remove('d-none');
        }
    } catch (error) {
        spinner.classList.add('d-none');
        submitBtn.classList.remove('d-none');

        // Переводим английские ошибки на русский
        let errorMessage = error.message;

        if (errorMessage.includes('invalid-verification-code')) {
            errorMessage = 'Неверный код подтверждения';
        } else if (errorMessage.includes('network')) {
            errorMessage = 'Ошибка сети';
        }

        errorDiv.textContent = errorMessage;
        errorDiv.classList.remove('d-none');
    }
});