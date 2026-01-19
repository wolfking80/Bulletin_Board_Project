import { postAction } from './utils.js';

function initFavorites() {
  document.querySelectorAll('.fav-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const data = await postAction(btn.dataset.url);
            
      if (data) {
      // Меняем цвет
        btn.classList.toggle('btn-warning', data.is_favorite);
        btn.classList.toggle('btn-outline-warning', !data.is_favorite);

      // Удаляем карточку, если мы на странице избранного
      if (btn.dataset.isFavoritesPage === 'True' && !data.is_favorite) {
        btn.closest('.ad-card-container').remove();
      }
    }
  });
});
}
document.addEventListener('DOMContentLoaded', initFavorites);