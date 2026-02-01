import { getAction } from "./utils.js";
import { formatDatesInHTML } from "./format_to_local_date.js";

class BatchLoader {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.offset = Number(this.container.dataset.initialOffset);
    this.hasMore = this.container.dataset.hasMore === 'True';
    this.batchSize = Number(this.container.dataset.batchSize);
    this.loadMoreUrl = this.container.dataset.loadMoreUrl;
    this.loading = false;

    this.init();
  }

  init() {
    window.addEventListener('scroll', () => {
      if ((window.scrollY + window.innerHeight) > (document.documentElement.scrollHeight - 200)) {
        this.loadMore();
      }
    });
  }

  async loadMore() {
    if (this.loading || !this.hasMore) return;

    this.loading = true;
    this.showLoadingSpinner();

    try {
    // Подхватываем текущие фильтры, чтобы не грузить лишнее
    const params = window.location.search.replace('?', '&');
    const isFav = this.container.dataset.isFavorites === 'True' ? '&is_fav=1' : '';
    const url = `${this.loadMoreUrl}?offset=${this.offset}${params}${isFav}`;

    const data = await getAction(url);

    if (data && data.html) {
      // ФОРМАТИРУЕМ ДАТЫ ПЕРЕД ВСТАВКОЙ
      const formattedHtml = formatDatesInHTML(data.html);
      // ищем .row внутри контейнера
      const row = this.container.querySelector('.row');
      
      if (row) {
        // Вставляем карточки ВНУТРЬ ряда, чтобы Bootstrap их выровнял
        row.insertAdjacentHTML("beforeend", formattedHtml);
      } else {
        this.container.insertAdjacentHTML("beforeend",formattedHtml);
      }

      this.offset += this.batchSize;
      this.hasMore = data.has_more;
    }
  } catch (error) {
    console.error("Ошибка загрузки:", error);
  } finally {
    this.loading = false;
    this.hideLoadingSpinner();
  }
}

  showLoadingSpinner() {
    document.getElementById("loadingSpinner")?.classList.remove("d-none");
  }

  hideLoadingSpinner() {
    document.getElementById("loadingSpinner")?.classList.add("d-none");
  }
}

export default BatchLoader;