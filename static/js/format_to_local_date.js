export function formatDate(el) {
  el.textContent = new Date(el.textContent).toLocaleString();
}

export function formatDatesInHTML(htmlString) {
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = htmlString;
  
  tempDiv.querySelectorAll(".date-field").forEach(el => {
    formatDate(el);
  });
  
  return tempDiv.innerHTML;
}

document.querySelectorAll(".date-field").forEach(el => {
  formatDate(el);
});