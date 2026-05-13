/**
 * Превращает ISO дату из БД в красивую локальную строку
 */
export function formatDate(el) {
  const rawDate = el.textContent.trim();
  if (!rawDate) return;

  const date = new Date(rawDate);

  // Проверка на валидность даты
  if (!isNaN(date.getTime())) {
    el.textContent = date.toLocaleString(undefined, {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}

/**
 * Используется BatchLoader-ом для обработки динамически подгруженного HTML
 */
export function formatDatesInHTML(htmlString) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlString, 'text/html');

  doc.querySelectorAll(".date-field").forEach(formatDate);

  return doc.body.innerHTML;
}

/**
 * Запуск для статического контента при первой загрузке
 */
export function initDateFormatting() {
  document.querySelectorAll(".date-field").forEach(formatDate);
}

// Если скрипт подключен не как модуль, запускаем сразу
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDateFormatting);
} else {
  initDateFormatting();
}
