import { postAction } from './utils.js';
import { formatDate } from './format_to_local_date.js';

class QuestionManager {
  constructor() {
    this.init();
  }

  init() {
    // Основная форма вопроса (которая под объявлением)
    const questionForm = document.getElementById('questionForm');
    if (questionForm) {
      questionForm.addEventListener('submit', (e) => this.handleMainSubmit(e));
    }

    // Делегирование кликов (Ответить / Отмена)
    document.addEventListener('click', (e) => {
      const replyBtn = e.target.closest('.reply-btn');
      if (replyBtn) this.handleReplyClick(replyBtn);

      const cancelBtn = e.target.closest('.cancel-reply-btn');
      if (cancelBtn) this.handleCancelReplyClick(cancelBtn);
    });

    // Делегирование отправки форм-ответов
    document.addEventListener('submit', (e) => {
      const replyForm = e.target.closest('.reply-form');
      if (replyForm) {
        e.preventDefault();
        this.handleReplyFormSubmit(replyForm);
      }
    });
  }

  // Логика главного вопроса
  async handleMainSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const url = form.dataset.addQuestionUrl;
    const errorEl = document.getElementById('questionErrors');
    // Скрываем предыдущие ошибки
    if (errorEl) {
        errorEl.classList.add('d-none');
        errorEl.textContent = '';
    }

    try {
      const data = await postAction(url, formData);
      if (data.success) {
        form.querySelector('textarea').value = '';
        const list = document.getElementById('questionsList');

        // Убираем заглушку "Вопросов нет"
        const empty = list.querySelector('#emptyMessage');
        if (empty) empty.remove();

        // Вставляем новый вопрос В НАЧАЛО
        list.insertAdjacentHTML('afterbegin', data.question_html);
        formatDate(list.firstElementChild.querySelector('.date-field'));

        // Сдвигаем offset лоадера, чтобы не было дублей при дозагрузке
        if (window.questionsBatchLoader) {
          window.questionsBatchLoader.offset += 1;
        }
        // Обновляем счетчик вопросов в заголовке
        this.updateCounter(data.questions_count);
      } else {
        errorEl.textContent = data.error;
        errorEl.classList.remove('d-none');
      }
    } catch (err) {
      console.error(err);
      if (errorEl) {
          errorEl.textContent = 'Ошибка соединения с сервером';
          errorEl.classList.remove('d-none');
      }
    }
  }

  // Логика ответа на вопрос
  async handleReplyFormSubmit(form) {
    const textarea = form.querySelector('textarea');
    const formData = new FormData();
    formData.append('text', textarea.value.trim());
    formData.append('parent_id', form.dataset.parentId);
    const url = form.dataset.addQuestionUrl;

    const data = await postAction(url, formData);
    if (data.success) {
      // Очищаем текстовое поле и скрываем форму
      textarea.value = '';
      form.closest('.reply-form-container').classList.add('d-none');

      // Вставляем ответ В КОНЕЦ ветки текущего вопроса
      const container = form.closest('.question-container').querySelector('.replies');
      container.insertAdjacentHTML('beforeend', data.question_html);
      // Форматируем дату нового ответа
      formatDate(container.lastElementChild.querySelector('.date-field'));
      // Обновляем счетчик вопросов в заголовке
      this.updateCounter(data.questions_count);
    } else {
      alert(data.error);
    }
  }

  handleReplyClick(btn) {
    const formContainer = document.getElementById(`replyForm${btn.dataset.questionId}`);
    // Скрываем все другие открытые формы
    document.querySelectorAll('.reply-form-container').forEach(el => el.classList.add('d-none'));
    // Показываем текущую форму
    formContainer.classList.remove('d-none');
    // Фокусируемся на текстовом поле
    formContainer.querySelector('textarea').focus();
  }

  handleCancelReplyClick(btn) {
    const container = btn.closest('.reply-form-container');
    container.classList.add('d-none');
    container.querySelector('textarea').value = '';
  }

  updateCounter(count) {
    const title = document.querySelector('#questionsTitle');
    if (title) title.textContent = `Вопросы и ответы (${count})`;
  }
}

new QuestionManager();