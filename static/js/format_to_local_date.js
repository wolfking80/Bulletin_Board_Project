document.querySelectorAll(".date-field").forEach(el => {
  el.textContent = new Date(el.textContent).toLocaleString();
});