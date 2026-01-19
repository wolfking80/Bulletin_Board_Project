import { postAction } from './utils.js';

function initRating() {
  const btns = document.querySelectorAll('.rating-btn');

  btns.forEach(btn => {
    btn.addEventListener('click', async (event) => {
      event.preventDefault();
      const data = await postAction(btn.dataset.url);

      if (data) {
        // 1. Обновляем цифры и процент (по ID)
        document.getElementById('pos-count').innerText = data.pos;
        document.getElementById('neg-count').innerText = data.neg;

        const percentSpan = document.getElementById('trust-percent');
        const posBar = document.getElementById('pos-bar');
        const negBar = document.getElementById('neg-bar');

        if (percentSpan) percentSpan.innerText = data.trust_percent;

        // Логика двух полосок
        const total = data.pos + data.neg;
        if (posBar && negBar) {
          if (total > 0) {
            posBar.style.width = data.trust_percent + '%';
            negBar.style.width = (100 - data.trust_percent) + '%';
          } else {
              posBar.style.width = '0%';
              negBar.style.width = '0%';
        }
      }

        // 2. Перекрашиваем кнопки более универсальным способом
        // Находим все кнопки рейтинга на странице
        const allButtons = document.querySelectorAll('.rating-btn');
        allButtons.forEach(rb => {
          const isPlus = rb.dataset.url.includes('plus');

          if (isPlus) {
            rb.classList.toggle('btn-success', data.user_choice === 'plus');
            rb.classList.toggle('btn-outline-success', data.user_choice !== 'plus');
          } else {
            rb.classList.toggle('btn-danger', data.user_choice === 'minus');
            rb.classList.toggle('btn-outline-danger', data.user_choice !== 'minus');
          }
        });
      }
    });
  });
}
document.addEventListener('DOMContentLoaded', initRating);