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

  init() {
    if (this.triggerType === 'scroll') {
      window.addEventListener('scroll', () => {
        if ((window.scrollY + window.innerHeight) > (document.documentElement.scrollHeight - 200)) {
          this.loadMore();
        }
      });
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
      const isFav = this.container.dataset.isFavorites === 'True' ? '&is_fav=1' : '';
      const url = `${this.loadMoreUrl}?offset=${this.offset}${params}${isFav}`;

      const data = await getAction(url);

      if (data && data.html) {
        const formattedHtml = formatDatesInHTML(data.html);
      // универсальная точка вставки - подгружаем карточки в «ряд» на главной и вопросы списком в деталях
        const row = this.container.querySelector('.row') || this.container;

        row.insertAdjacentHTML("beforeend", formattedHtml);

        this.offset += this.batchSize;
        this.hasMore = data.has_more;
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