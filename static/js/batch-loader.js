import { getAction } from "./utils.js";
import { formatDatesInHTML } from "./format_to_local_date.js";

class BatchLoader {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;

    this.offset = Number(this.container.dataset.initialOffset);
    this.hasMore = this.container.dataset.hasMore === 'True';
    this.batchSize = Number(this.container.dataset.batchSize);
    this.loadMoreUrl = this.container.dataset.loadMoreUrl;
    this.loading = false;

    // Тип триггера
    this.triggerType = this.container.dataset.triggerType;
    this.loadMoreBtn = document.getElementById(this.container.dataset.loadMoreBtnId);

    this.init();
  }

  async checkFullFill() {
  // Даем браузеру 100мс на отрисовку новых карточек
  setTimeout(async () => {
    const dh = document.documentElement.scrollHeight;
    const wh = window.innerHeight;

    // Если данных еще много, а скролл так и не появился (или он короче 100px)
    if (this.hasMore && !this.loading && dh <= wh + 100) {
      await this.loadMore();
    }
  }, 100); 
}

  init() {
    if (this.triggerType === 'scroll') {
      window.addEventListener('scroll', () => {
        if ((window.scrollY + window.innerHeight) > (document.documentElement.scrollHeight - 200)) {
          this.loadMore();
        }
      });
      this.checkFullFill(); 
    } else if (this.triggerType === 'button' && this.loadMoreBtn) {
      this.loadMoreBtn.addEventListener('click', () => this.loadMore());
    }
  }

  async loadMore() {
    if (this.loading || !this.hasMore) return;

    this.loading = true;
    this.toggleInterface(true); // Скрываем кнопку/показываем спиннер

    try {
      const params = window.location.search.replace('?', '&');
      const ownerId = this.container.dataset.ownerId ? `&owner_id=${this.container.dataset.ownerId}` : '';
      const showAll = this.container.dataset.showAll === 'True' ? `&show_all=1` : '';
      const isFav = this.container.dataset.isFavorites === 'True' ? '&is_fav=1' : '';
      const url = `${this.loadMoreUrl}?offset=${this.offset}${params}${isFav}${ownerId}${showAll}`;

      const data = await getAction(url);

      if (data && data.html) {
        const formattedHtml = formatDatesInHTML(data.html);
      // универсальная точка вставки - подгружаем карточки в «ряд» на главной и вопросы списком в деталях
        const row = this.container.querySelector('.row') || this.container;

        // создаем временный «виртуальный» элемент для разбора строки
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = formattedHtml;

    // находим все новые карточки в этом куске
        const newCards = tempDiv.querySelectorAll('.ad-card-container');
        let addedCount = 0;

        newCards.forEach(card => {
        const cardId = card.querySelector('.card')?.id;
        
        // ПРОВЕРКА: вставляем только если такого ID еще нет на странице
        if (cardId && !document.getElementById(cardId)) {
            row.appendChild(card); // Вместо insertAdjacentHTML используем appendChild
            addedCount++;
          }
        });

    // КОРРЕКТИРОВКА: увеличиваем смещение только на РЕАЛЬНО добавленные
    // Это исключает «исчезновение» объявлений при 20+ ТОПах
        this.offset += addedCount;
        this.hasMore = data.has_more;

        // ПРОВЕРКА: если после вставки всё еще нет скролла — зовем loadMore снова
        if (this.hasMore) {
          this.checkFullFill();
        }
      }
    } catch (error) {
      console.error("Ошибка загрузки:", error);
    } finally {
      this.loading = false;
      this.toggleInterface(false); // Возвращаем кнопку, если есть еще данные
    }
  }

  // Управление кнопкой и спиннером
  toggleInterface(isLoading) {
    const spinner = document.getElementById("loadingSpinner");

    if (isLoading) {
      spinner?.classList.remove("d-none");
      if (this.triggerType === 'button') this.loadMoreBtn?.classList.add("d-none");
    } else {
      spinner?.classList.add("d-none");
      // Показываем кнопку снова, только если данные еще остались
      if (this.triggerType === 'button' && this.hasMore) {
        this.loadMoreBtn?.classList.remove("d-none");
      } else if (this.triggerType === 'button' && !this.hasMore) {
        this.loadMoreBtn?.remove(); // Если больше нет, кнопку больше не показываем
      }
    }
  }
}

export default BatchLoader;