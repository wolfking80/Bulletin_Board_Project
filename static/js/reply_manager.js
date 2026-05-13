import { postAction } from './utils.js';
import { formatDate } from './format_to_local_date.js';

// Инициализируем лоадер (он подхватит настройки из data-атрибутов)
const questionsBatchLoader = document.getElementById('questionsList')
  ? new (await import('./batch-loader.js')).default('questionsList')
  : null;

class QuestionManager {
  constructor() {
    this.init();
  }

  init() {
    // Делегирование кликов
    document.addEventListener('click', (e) => {
      const replyBtn = e.target.closest('.reply-btn');
      if (replyBtn) return this.handleReplyClick(replyBtn);

      const cancelBtn = e.target.closest('.cancel-reply-btn');
      if (cancelBtn) return this.handleCancelReplyClick(cancelBtn);
    });

    // Единый обработчик отправок
    document.addEventListener('submit', (e) => {
      const form = e.target;
      if (form.id === 'questionForm') {
        e.preventDefault();
        this.handleMainSubmit(form);
      } else if (form.classList.contains('reply-form')) {
        e.preventDefault();
        this.handleReplyFormSubmit(form);
      }
    });
  }

  async handleMainSubmit(form) {
    // собираем все данные из полей формы
    const formData = new FormData(form);
    const url = form.dataset.addQuestionUrl;
    const errorEl = document.getElementById('questionErrors');
    const submitBtn = form.querySelector('button[type="submit"]');
    // Скрываем блок с ошибками (если они горели от предыдущей неудачной попытки)
    this.toggleError(errorEl, null);
    // Блокируем кнопку отправки, пока идет сетевой запрос
    submitBtn.disabled = true;

    try {
      const data = await postAction(url, formData);
      // Если успешное сохранение вопроса
      if (data?.success) {
      // Очищаем текстовое поле формы  
        form.reset();

        const list = document.getElementById('questionsList');

        // Удаляем сообщение о пустоте
        list.querySelector('#emptyMessage')?.remove();

        // Вставляем и форматируем
        list.insertAdjacentHTML('afterbegin', data.question_html);
        formatDate(list.firstElementChild.querySelector('.date-field'));

        // Если на странице работает пагинатор (BatchLoader), 
        // JS увеличивает его внутреннее смещение (offset) на 1. 
        // Это нужно, чтобы при следующем скролле пагинатор 
        // не подгрузил с сервера дубликат из-за сдвига базы данных
        if (questionsBatchLoader) questionsBatchLoader.offset += 1;

        this.updateCounter(data.questions_count);
      } else {
        this.toggleError(errorEl, data.error || 'Ошибка валидации');
      }
    } catch (err) {
      this.toggleError(errorEl, 'Ошибка соединения с сервером');
    } finally {
      submitBtn.disabled = false;
    }
  }

  async handleReplyFormSubmit(form) {
    const textarea = form.querySelector('textarea');
    const text = textarea.value.trim();
    if (!text) return;

    const formData = new FormData();
    formData.append('text', text);
    formData.append('parent_id', form.dataset.parentId);

    const data = await postAction(form.dataset.addQuestionUrl, formData);

    if (data?.success) {
      form.reset();
      form.closest('.reply-form-container').classList.add('d-none');
      
      // Находим блок существующих ответов (.replies) именно внутри карточки текущего вопроса
      const repliesContainer = form.closest('.question-container').querySelector('.replies');
      // Вставляем новый ответ в самый конец списка ответов
      repliesContainer.insertAdjacentHTML('beforeend', data.question_html);
      formatDate(repliesContainer.lastElementChild.querySelector('.date-field'));

      this.updateCounter(data.questions_count);
    } else {
      alert(data.error);
    }
  }

  handleReplyClick(btn) {
    const formContainer = document.getElementById(`replyForm${btn.dataset.questionId}`);
    // Находит все формы ответов на странице и закрывает их, 
    // чтобы на экране была открыта строго одна форма за раз
    document.querySelectorAll('.reply-form-container').forEach(el => el.classList.add('d-none'));
    // Открываем форму ответа для выбранного вопроса
    formContainer?.classList.remove('d-none');
    // Автоматически ставит курсор мыши в текстовое поле, 
    // чтобы пользователь мог сразу печатать текст
    formContainer?.querySelector('textarea')?.focus();
  }
  
  // Срабатывает при клике на «Отмена». 
  // Прячет форму ответа и полностью очищает набранный текст
  handleCancelReplyClick(btn) {
    const container = btn.closest('.reply-form-container');
    container.classList.add('d-none');
    container.querySelector('textarea').value = '';
  }

  toggleError(el, message) {
    if (!el) return;
    el.textContent = message || '';
    el.classList.toggle('d-none', !message);
  }

  updateCounter(count) {
    const title = document.querySelector('#questionsTitle');
    if (title) title.textContent = `Вопросы и ответы (${count})`;
  }
}

new QuestionManager();