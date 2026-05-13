import { postAction } from './utils.js';

function initFavorites() {
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.fav-btn');
    if (!btn) return;

    e.preventDefault();

    // Блокируем кнопку на время запроса, чтобы избежать "дабл-кликов"
    if (btn.disabled) return;
    btn.disabled = true;

    const data = await postAction(btn.dataset.url);

    if (data && !data.error) {
      // Обновляем визуальное состояние кнопки
      // Используем data.is_favorite напрямую для точности
      if (data.is_favorite) {
        btn.classList.replace('btn-outline-warning', 'btn-warning');
      } else {
        btn.classList.replace('btn-warning', 'btn-outline-warning');
      }

      // Обновляем счетчик лайков
      const countSpan = btn.querySelector('.fav-count');
      if (countSpan && typeof data.fav_count !== 'undefined') {
        countSpan.textContent = data.fav_count;
      }

      // Логика для страницы "Мои избранные"
      const adsContainer = document.getElementById('adsContainer');
      const isFavPage = adsContainer?.dataset.isFavorites === 'True';

      if (isFavPage && !data.is_favorite) {
        const card = btn.closest('.ad-card-container');
        if (card) {
          // Добавляем плавное исчезновение перед удалением
          card.style.opacity = '0';
          card.style.transform = 'scale(0.9)';
          card.style.transition = '0.3s all ease';
          setTimeout(() => card.remove(), 300);
        }
      }
    }

    btn.disabled = false;
  });
}

document.addEventListener('DOMContentLoaded', initFavorites);