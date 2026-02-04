import { postAction } from './utils.js';
import { formatDate } from './format_to_local_date.js';

class ReplyManager {
  constructor() {
    this.init();
  }

  init() {
    document.addEventListener('click', (e) => {
      // Клик по "Ответить"
      const replyBtn = e.target.closest('.reply-btn');
      if (replyBtn) {
        this.handleReplyClick(replyBtn);
      }

      // Клик по "Отмена"
      const cancelBtn = e.target.closest('.cancel-reply-btn');
      if (cancelBtn) {
        this.handleCancelReplyClick(cancelBtn);
      }
    });

    document.addEventListener('submit', (e) => {
      // Отправка формы ответа
      const replyForm = e.target.closest('.reply-form');
      if (replyForm) {
        e.preventDefault();
        this.handleReplyFormSubmit(replyForm);
      }
    });
  }

  handleReplyClick(replyBtn) {
    const formContainer = document.getElementById(`replyForm${replyBtn.dataset.questionId}`);

    // Скрываем все открытые формы ответов, чтобы не мусорить на экране
    document.querySelectorAll('.reply-form-container').forEach(form => {
      form.classList.add('d-none');
    });

    if (formContainer) {
      formContainer.classList.remove('d-none');
      formContainer.querySelector('textarea').focus();
    }
  }

  handleCancelReplyClick(cancelBtn) {
    const formContainer = cancelBtn.closest('.reply-form-container');
    if (formContainer) {
      formContainer.classList.add('d-none');
      formContainer.querySelector('textarea').value = '';
    }
  }

  async handleReplyFormSubmit(formElement) {
    const textarea = formElement.querySelector('textarea');
    const text = textarea.value.trim();
    const parentId = formElement.dataset.parentId;
    const url = formElement.dataset.addQuestionUrl;

    if (!text) return;

    const formData = new FormData();
    formData.append('text', text);
    formData.append('parent_id', parentId);

    const data = await postAction(url, formData);

    if (data && data.success) {
      textarea.value = '';
      formElement.closest('.reply-form-container').classList.add('d-none');

      // Ищем контейнер именно для веток ответов внутри текущего вопроса
      const repliesContainer = formElement.closest('.question-container').querySelector('.replies');
      
      // Вставляем ответ (question_html из ответа вьюшки)
      repliesContainer.insertAdjacentHTML('beforeend', data.question_html);

      // Форматируем дату в только что добавленном ответе
      const newReply = repliesContainer.lastElementChild;
      const dateEl = newReply.querySelector('.date-field');
      if (dateEl) formatDate(dateEl);

      // Обновляем общий счетчик в заголовке
      const titleEl = document.querySelector('#questionsTitle');
      if (titleEl) {
        titleEl.textContent = `Вопросы и ответы (${data.questions_count})`;
      }
    } else {
      alert(data ? data.error : "Ошибка при отправке ответа");
    }
  }
}
// Запускаем менеджер
new ReplyManager();