import BatchLoader from './batch-loader.js';

// Запуск бесконечного скролла для объявлений (если контейнер есть на странице)
if (document.getElementById("adsContainer")) {
    new BatchLoader("adsContainer");
}

// Запуск подгрузки вопросов по кнопке на странице деталей объявления
if (document.getElementById("questionsList")) {
    new BatchLoader("questionsList");
}