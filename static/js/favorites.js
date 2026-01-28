import { postAction } from './utils.js';

function initFavorites() {
  // Вешаем обработчик на документ, чтобы ловить клики даже на новых карточках
  document.addEventListener('click', async (e) => {
  // Ищем ближайшую кнопку с классом .fav-btn от места клика
    const btn = e.target.closest('.fav-btn');
    
  // Если клик был не по кнопке избранного — ничего не делаем
  if (!btn) return;

  e.preventDefault();
    
  // Отправляем запрос на сервер
  const data = await postAction(btn.dataset.url);
            
  if (data) {
  // Переключаем классы оформления (желтая заливка / контур)
    btn.classList.toggle('btn-warning', data.is_favorite);
    btn.classList.toggle('btn-outline-warning', !data.is_favorite);

  // Логика удаления карточки именно на странице избранного
  if (btn.dataset.isFavoritesPage === 'True' && !data.is_favorite) {
    const card = btn.closest('.ad-card-container');
  if (card) {
    card.remove();
      }
    }
  }
});
}

// запуск функции только когда браузер построит всю структуру страницы (DOM), иначе скрипт не найдет кнопки
document.addEventListener('DOMContentLoaded', initFavorites);