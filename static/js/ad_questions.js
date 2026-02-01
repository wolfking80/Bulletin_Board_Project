import { postAction } from './utils.js';
import { formatDate } from './format_to_local_date.js';

const questionForm = document.getElementById('questionForm');
if (questionForm) {
  questionForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    const url = this.dataset.addQuestionUrl;
    const errorEl = document.getElementById('questionErrors');

    try {
      const data = await postAction(url, formData);
      if (data.success) {
        this.querySelector('textarea').value = '';
        errorEl.classList.add('d-none');

        const list = document.getElementById('questionsList');
        const empty = list.querySelector('#emptyMessage');
        if (empty) empty.remove();

        list.insertAdjacentHTML('afterbegin', data.question_html);

        // Форматируем дату в новом вопросе
        formatDate(list.firstElementChild.querySelector('.date-field'));

        document.getElementById('questionsTitle').textContent = `Вопросы по товару (${data.questions_count})`;
      } else {
        errorEl.textContent = data.error;
        errorEl.classList.remove('d-none');
      }
    } catch (err) {
      console.error(err);
    }
  });
}