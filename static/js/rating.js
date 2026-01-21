import { postAction } from './utils.js';

function initRating() {
  const btns = document.querySelectorAll('.rating-btn');   // находим на странице все элементы с классом .rating-btn

  btns.forEach(btn => {                                   // в цикле вешаем обработчик события на каждую найденную кнопку
    btn.addEventListener('click', async (event) => {      // async, так как внутри будем ждать ответа от сервера
      event.preventDefault();                             // убираем перезагрузку страницы (стандартное поведение)
      const data = await postAction(btn.dataset.url);     // вызываем функцию отправки запроса. URL берем из атрибута кнопки data-url
                                                          // Ждем (await), пока сервер пришлет данные (JSON)

      if (data) {                                         // если сервер ответил успешно и прислал данные
        // 1. Обновляем цифры и процент (по ID)
        document.getElementById('pos-count').innerText = data.pos;  // находим спан с числом лайков и мгновенно меняем цифру на ту, что прислал сервер
        document.getElementById('neg-count').innerText = data.neg;  // то же самое для числа дизлайков

        const percentSpan = document.getElementById('trust-percent');   // находим текстовый рейтинг и две части полоски (зеленую и красную)
        const posBar = document.getElementById('pos-bar');
        const negBar = document.getElementById('neg-bar');

        if (percentSpan) percentSpan.innerText = data.trust_percent;    // если текстовое поле процента есть на странице, обновляем в нем число

        // Логика двух полосок
        const total = data.pos + data.neg;         // считаем общее количество голосов
        if (posBar && negBar) {                    // проверяем наличие полосок
          if (total > 0) {                         // если есть хотя бы один голос
            posBar.style.width = data.trust_percent + '%';             // меняем ширину зеленой полоски
            negBar.style.width = (100 - data.trust_percent) + '%';     // красная полоска всегда занимает оставшееся место
          } else {                                                     // если голосов ноль, обнуляем ширину обеих полосок, чтобы они исчезли
              posBar.style.width = '0%';
              negBar.style.width = '0%';
        }
      }

        // 2. Перекрашиваем кнопки более универсальным способом
        // Находим все кнопки рейтинга на странице
        const allButtons = document.querySelectorAll('.rating-btn');    // снова находим кнопки, чтобы обновить их внешний вид (закрашена или нет)
        allButtons.forEach(rb => {                                      // перебираем их
          const isPlus = rb.dataset.url.includes('plus');               // определяем, какая это кнопка (плюс или минус) по её URL

          if (isPlus) {
            rb.classList.toggle('btn-success', data.user_choice === 'plus');         // если юзер нажал «плюс», кнопка станет закрашенной (btn-success). Если нет — класс удалится
            rb.classList.toggle('btn-outline-success', data.user_choice !== 'plus'); // и наоборот: если кнопка не активна, она становится контурной
          } else {
            rb.classList.toggle('btn-danger', data.user_choice === 'minus');         // аналогично для кнопки дизлайка (btn-danger)
            rb.classList.toggle('btn-outline-danger', data.user_choice !== 'minus');
          }
        });
      }
    });
  });
}
document.addEventListener('DOMContentLoaded', initRating);     // запускаем функцию initRating только тогда, когда весь HTML-код страницы полностью загрузится