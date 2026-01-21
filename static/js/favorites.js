import { postAction } from './utils.js';

function initFavorites() {
  document.querySelectorAll('.fav-btn').forEach(btn => {  // находим все элементы с классом .fav-btn (звездочки в карточках) и для каждого запускаем цикл
    btn.addEventListener('click', async (e) => {          // ловим клик. async , так как делаем сетевой запрос.
      e.preventDefault();                                 // блокируем стандартное поведение
      const data = await postAction(btn.dataset.url);     // вызываем postAction, передаем ей URL из атрибута data-url, ждем (await) ответа от сервера в формате JSON
            
      if (data) {                                         // если сервер ответил успешно
      // Меняем цвет
        btn.classList.toggle('btn-warning', data.is_favorite);  // если сервер прислал is_favorite: true, кнопке добавляется класс btn-warning (закрашенная желтая). Если false — класс удаляется
        btn.classList.toggle('btn-outline-warning', !data.is_favorite);  // и наоборот: если товар не в избранном, кнопка становится контурной (btn-outline-warning)

      // Удаляем карточку, если мы на странице избранного
      if (btn.dataset.isFavoritesPage === 'True' && !data.is_favorite) {  // проверяем атрибут data-is-favorites-page из Django-шаблона и что товар только что был удален из избранного (!data.is_favorite).
        btn.closest('.ad-card-container').remove();                       //ищем ближайшего родителя с классом .ad-card-container (всю карточку целиком) и мгновенно удаляем её из HTML-дерева
      }
    }
  });
});
}
document.addEventListener('DOMContentLoaded', initFavorites);  // запуск функции только когда браузер построит всю структуру страницы (DOM), иначе скрипт не найдет кнопки