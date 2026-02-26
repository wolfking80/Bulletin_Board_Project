import { postAction } from './utils.js';

async function handleToggleNotif(btn) {
  const url = btn.getAttribute('data-url');
  const data = await postAction(url);

  if (data) {
    const isEnabled = data.notifications_enabled;

    // Текст кнопки и её цвет (danger для "отключить", success для "включить")
    const btnText = btn.querySelector('#btn-text');
    if (btnText) btnText.innerText = isEnabled ? 'Отключить' : 'Включить';
    btn.className = `btn ${isEnabled ? 'btn-outline-danger' : 'btn-outline-success'}`;

    // Текст описания в карточке
    const textElem = document.getElementById('notif-text');
    if (textElem) {
      textElem.innerText = isEnabled
        ? 'Вы получаете уведомления о статусе ваших объявлений (VIP, Топ, Модерация).'
        : 'Уведомления отключены. Вы не узнаете об изменении статуса ваших объявлений.';
    }

    // Иконка и цвет круга (bg-success если включено, bg-secondary если выключено)
    const iconWrapper = document.getElementById('notif-icon-bg');
    const icon = document.getElementById('notif-icon');

    if (iconWrapper) {
      iconWrapper.className = `icon-wrapper ${isEnabled ? 'bg-success' : 'bg-secondary'} text-white rounded-circle me-3`;
    }
    if (icon) {
      icon.className = `bi ${isEnabled ? 'bi-bell-fill' : 'bi-bell-slash'}`;
    }
  }
}

// Делаем функцию доступной для HTML-атрибутов onclick
window.handleToggleNotif = handleToggleNotif;