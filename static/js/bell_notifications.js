import { getAction, postAction } from '/static/js/utils.js';

// Обновление счетчика на колокольчике
function updateBellCounter(count) {
  const badge = document.getElementById('notif-badge');
  if (count > 0) {
    if (badge) {
      badge.textContent = count > 99 ? '99+' : count;
    } else {
      const bell = document.querySelector('.notification-bell');
      if (bell) {
        const newBadge = document.createElement('span');
        newBadge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger';
        newBadge.id = 'notif-badge';
        newBadge.textContent = count > 99 ? '99+' : count;
        bell.appendChild(newBadge);

        // Анимация при новых
        bell.classList.add('bell-shake');
        setTimeout(() => bell.classList.remove('bell-shake'), 1000);
      }
    }
  } else {
    if (badge) badge.remove();
  }
}

// Загрузка списка уведомлений в выпадашку
async function loadNotificationsList() {
  const container = document.getElementById('dropdown-notifications-list');
  if (!container) return;

  container.innerHTML = '<div class="text-center py-3">Загрузка...</div>';

  const data = await getAction('/profile/notifications/');

  if (!data) {
    container.innerHTML = '<div class="text-center py-3 text-danger">Ошибка загрузки</div>';
    return;
  }

  container.innerHTML = '';

  if (data.notifications.length === 0) {
    container.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-bell-slash fs-1 text-muted"></i>
                <p class="text-muted mt-2">Нет уведомлений</p>
            </div>
        `;
  } else {
    data.notifications.forEach(n => {
      const item = document.createElement('div');
      item.className = `notification-item p-3 border-bottom ${!n.is_read ? 'bg-light' : ''}`;
      item.style.cursor = 'pointer';
      item.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="d-flex align-items-center gap-2 mb-1">
                            <small class="text-muted">${n.created_at}</small>
                            <span class="badge bg-secondary">${n.type}</span>
                        </div>
                        <p class="mb-1">${n.message}</p>
                        ${!n.is_read ? `
                            <button class="btn btn-sm btn-link p-0 mark-read-btn" data-id="${n.id}">
                                Отметить прочитанным
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;
      container.appendChild(item);
    });

    // Обработчики для кнопок "отметить прочитанным"
    document.querySelectorAll('.mark-read-btn').forEach(btn => {
      btn.addEventListener('click', async function (e) {
        e.stopPropagation();
        const result = await postAction(`/profile/notifications/mark-read/${this.dataset.id}/`);
        if (result && !result.error) {
          updateBellCounter(result.unread_count);
          loadNotificationsList();
        }
      });
    });
  }
}

// Отметить все как прочитанные
async function markAllAsRead() {
  const result = await postAction('/profile/notifications/mark-all-read/');
  if (result && !result.error) {
    updateBellCounter(0);
    loadNotificationsList();
  }
}

// Проверка новых уведомлений (polling)
async function checkNewNotifications() {
  const data = await getAction('/profile/notifications/unread-count/');
  if (data) {
    updateBellCounter(data.unread_count);
  }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
  const bell = document.getElementById('notificationsDropdownBtn');
  const dropdown = document.getElementById('notificationsDropdown');

  if (bell && dropdown) {
    // Открытие/закрытие при клике
    bell.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();

      if (dropdown.classList.contains('show')) {
        dropdown.classList.remove('show');
      } else {
        // Загружаем уведомления перед открытием
        loadNotificationsList();
        dropdown.classList.add('show');
      }
    });

    // Закрытие при клике вне
    document.addEventListener('click', function (e) {
      if (!bell.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.remove('show');
      }
    });

    // Кнопка "Отметить всё"
    const markAllBtn = document.querySelector('.mark-all-read-btn');
    if (markAllBtn) {
      markAllBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        markAllAsRead();
      });
    }

    // Запускаем проверку
    checkNewNotifications();
    setInterval(checkNewNotifications, 1250);
  }
});