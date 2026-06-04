import { postAction } from './utils.js';

// Удаление одного уведомления
document.querySelectorAll('.delete-one-btn').forEach(btn => {
  btn.addEventListener('click', async function() {
    const notificationId = this.dataset.id;
    if (confirm('Удалить уведомление?')) {
      const result = await postAction(`/profile/notifications/delete/${notificationId}/`);
      if (result && result.status === 'ok') {
        location.reload();
      }
    }
  });
});

// Удаление всех
const deleteAllBtn = document.getElementById('confirmDeleteAll');
if (deleteAllBtn) {
  deleteAllBtn.addEventListener('click', async function() {
    const result = await postAction('/profile/notifications/delete-all/');
    if (result && result.status === 'ok') {
      location.reload();
    }
  });
}