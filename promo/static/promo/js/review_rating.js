document.addEventListener('DOMContentLoaded', function() {
    const ratingContainer = document.querySelector('.rating');
    if (!ratingContainer) return;

    const stars = ratingContainer.querySelectorAll('.star-btn');
    const ratingInput = ratingContainer.querySelector('#id_rating_value');
    let selectedValue = 0;

    // Функция для окрашивания звезд до определенного индекса
    function highlightStars(count, className) {
        stars.forEach((star, index) => {
            if (index < count) {
                star.style.color = '#FFD700'; // Золотой цвет препода
                if (className) star.classList.add(className);
            } else {
                if (!star.classList.contains('selected')) {
                    star.style.color = '#ccc'; // Серый дефолтный цвет
                }
                if (className) star.classList.remove(className);
            }
        });
    }

    stars.forEach((star, index) => {
        // 1. Наведение мыши (Hover)
        star.addEventListener('mouseover', function() {
            highlightStars(index + 1, 'hovered');
        });

        // 2. Уход мыши (Восстанавливаем кликнутое состояние)
        star.addEventListener('mouseout', function() {
            stars.forEach(s => s.classList.remove('hovered'));
            highlightStars(selectedValue, null);
        });

        // 3. Клик (Жёсткая фиксация значения для отправки в Django)
        star.addEventListener('click', function() {
            selectedValue = index + 1;
            ratingInput.value = selectedValue; // Записываем цифру в форму!
            
            // Фиксируем класс selected
            stars.forEach((s, i) => {
                if (i < selectedValue) {
                    s.classList.add('selected');
                } else {
                    s.classList.remove('selected');
                }
            });
            highlightStars(selectedValue, null);
            console.log("Выбранный рейтинг зафиксирован в HTML:", ratingInput.value);
        });
    });
});
