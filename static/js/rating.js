import { postAction } from './utils.js';

function initRating() {
  const container = document.querySelector('.rating-stars-container');
  if (!container) return;

  container.addEventListener('click', async (e) => {
    const star = e.target.closest('.star-btn');
    if (!star) return;

    const score = parseInt(star.dataset.score);
    const url = container.dataset.url;

    const formData = new FormData();
    formData.append('score', score);

    const data = await postAction(url, formData);

    if (data && !data.error) {
      // Обновляем звезды голосования (целые)
      const interactiveStars = container.querySelectorAll('.star-btn');
      interactiveStars.forEach((s, index) => {
        if (index < data.user_score) {
          s.classList.replace('text-secondary', 'text-warning');
          s.classList.remove('opacity-50');
        } else {
          s.classList.replace('text-warning', 'text-secondary');
          s.classList.add('opacity-50');
        }
      });

      // Обновляем верхний золотой слой (точное закрашивание)
      const goldLayer = document.getElementById('stars-gold-layer');
      if (goldLayer) {
        const percent = (data.avg_rating * 20).toFixed(1);
        goldLayer.style.width = `${percent}%`;
      }

      // Обновляем текстовые цифры
      const avgEl = document.getElementById('avg-rating-display');
      const countEl = document.getElementById('total-votes-count');

      if (avgEl) avgEl.innerText = data.avg_rating;
      if (countEl) countEl.innerText = data.total_votes;
    }
  });
  // Устанавливаем начальную ширину при загрузке страницы
  const goldLayer = document.getElementById('stars-gold-layer');
  if (goldLayer) {
    // Берем число из data-avg (например, 4.6) и превращаем в %
    const avg = parseFloat(goldLayer.dataset.avg.replace(',', '.'));
    goldLayer.style.width = `${(avg * 20).toFixed(1)}%`;
  }
}

document.addEventListener('DOMContentLoaded', initRating);