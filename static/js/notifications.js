import { postAction } from './utils.js';

function initNotificationToggle() {
  const btn = document.querySelector('.toggle-notif-btn');
  if (!btn) return;

  btn.addEventListener('click', async (e) => {
    e.preventDefault();

    // Блокируем кнопку на время запроса
    if (btn.disabled) return;
    btn.disabled = true;

    const data = await postAction(btn.dataset.url);

    if (data && !data.error) {
      const isEnabled = data.notifications_enabled;

      // Обновляем текст и класс кнопки
      const btnText = btn.querySelector('#btn-text');
      if (btnText) {
        btnText.innerText = isEnabled ? 'Отключить' : 'Включить';
      }
      btn.className = `btn toggle-notif-btn ${isEnabled ? 'btn-outline-danger' : 'btn-outline-success'}`;

      // Обновляем описание
      const textElem = document.getElementById('notif-text');
      if (textElem) {
        textElem.innerText = isEnabled
          ? 'Вы получаете уведомления о статусе ваших объявлений (VIP, Топ, Модерация).'
          : 'Уведомления отключены. Вы не узнаете об изменении статуса ваших объявлений.';
      }

      // Обновляем иконку и её фон
      const iconWrapper = document.getElementById('notif-icon-bg');
      const icon = document.getElementById('notif-icon');

      if (iconWrapper) {
        iconWrapper.className = `icon-wrapper ${isEnabled ? 'bg-success' : 'bg-secondary'} text-white rounded-circle me-3`;
      }
      if (icon) {
        icon.className = `bi ${isEnabled ? 'bi-bell-fill' : 'bi-bell-slash'}`;
      }
    }

    btn.disabled = false;
  });
}

document.addEventListener('DOMContentLoaded', initNotificationToggle);
