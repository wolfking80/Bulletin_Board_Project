import { getAction } from "./utils.js";
import { formatDatesInHTML } from "./format_to_local_date.js";

class BatchLoader {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;

    // Инициализация данных из dataset
    const ds = this.container.dataset;
    this.offset = Number(ds.initialOffset);
    this.hasMore = ds.hasMore === 'True';
    this.loadMoreUrl = ds.loadMoreUrl;
    this.triggerType = ds.triggerType;
    this.loadMoreBtn = document.getElementById(ds.loadMoreBtnId);

    this.loading = false;
    this.init();
  }

  init() {
    if (this.triggerType === 'scroll') {
      // Используем throttle или простую проверку для оптимизации скролла
      window.addEventListener('scroll', () => {
        const threshold = document.documentElement.scrollHeight - window.innerHeight - 200;
        if (window.scrollY > threshold) this.loadMore();
      });
      this.checkFullFill();
    } else if (this.triggerType === 'button' && this.loadMoreBtn) {
      this.loadMoreBtn.addEventListener('click', () => this.loadMore());
    }
  }

  // Проверяем, заполнен ли экран. Если нет — подгружает еще.
  async checkFullFill() {
    if (this.triggerType === 'button') return;

    if (!this.hasMore || this.loading) return;

    // Ждем отрисовки (requestAnimationFrame лучше чем setTimeout)
    requestAnimationFrame(async () => {
      const dh = document.documentElement.scrollHeight;
      const wh = window.innerHeight;
      if (dh <= wh + 100) {
        await this.loadMore();
      }
    });
  }

  async loadMore() {
    if (this.loading || !this.hasMore) return;
    this.loading = true;
    this.toggleInterface(true);

    try {
      // Используем URLSearchParams для чистоты кода
      const urlParams = new URLSearchParams(window.location.search);
      urlParams.set('offset', this.offset);

      const ds = this.container.dataset;
      if (ds.ownerId) urlParams.set('owner_id', ds.ownerId);
      if (ds.showAll === 'True') urlParams.set('show_all', '1');
      if (ds.isFavorites === 'True') urlParams.set('is_fav', '1');

      if (ds.category) {
        urlParams.set('category', ds.category);
      }

      const url = `${this.loadMoreUrl}?${urlParams.toString()}`;
      const data = await getAction(url);

      if (data?.html) {
        this.renderBatch(data.html);
        this.hasMore = data.has_more;
        if (this.hasMore) this.checkFullFill();
      }
    } catch (error) {
      console.error("Ошибка загрузки batch:", error);
    } finally {
      this.loading = false;
      this.toggleInterface(false);
    }
  }

  renderBatch(html) {
    const target = this.container.querySelector('.row') || this.container;
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;

    // Ищем либо карточки объявлений, либо любые прямые элементы вопросов/ответов
    const newItems = tempDiv.querySelectorAll('.ad-card-container, .question-container, [id^="question-"]');

    // если кастомных классов нет, берем всех прямых потомков пришедшего HTML
    const itemsToAppend = newItems.length > 0 ? newItems : tempDiv.children;

    let addedCount = 0;
    Array.from(itemsToAppend).forEach(item => {
      // Проверяем на дубликаты по ID (чтобы не вставлять то, что уже есть в DOM)
      if (!item.id || !document.getElementById(item.id)) {
        target.appendChild(item);
        addedCount++;
      }
    });

    // Если сервер ничего не вернул, принудительно останавливаем лоадер
    if (addedCount === 0) {
      this.hasMore = false;
      this.container.dataset.hasMore = 'False';
      return;
    }

    this.offset += addedCount;
  }


  toggleInterface(isLoading) {
    const spinner = document.getElementById("loadingSpinner");
    spinner?.classList.toggle("d-none", !isLoading);

    if (this.triggerType === 'button' && this.loadMoreBtn) {
      this.loadMoreBtn.classList.toggle("d-none", isLoading || !this.hasMore);
      if (!this.hasMore && !isLoading) this.loadMoreBtn.remove();
    }
  }
}

export default BatchLoader;