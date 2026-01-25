const alerts = document.querySelectorAll('.auto-dismiss');

alerts.forEach(alert => {
  // Создаем экземпляр alert Bootstrap
  const bsAlert = new bootstrap.Alert(alert);
  
  // Автоматическое закрытие через 3 секунды
  setTimeout(() => {
    bsAlert.close();
  }, 3000);
});