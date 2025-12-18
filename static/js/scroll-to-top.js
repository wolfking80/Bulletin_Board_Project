const scrollBtn = document.getElementById("scrollToTopBtn");

scrollBtn.addEventListener("click", () => {
  if (!scrollBtn.classList.contains("disabled")) {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }
});

window.addEventListener("scroll", () => {
  if (window.scrollY > 300) {
    scrollBtn.classList.remove("disabled");
    scrollBtn.classList.add("show");
  } else {
    scrollBtn.classList.add("disabled");
    scrollBtn.classList.remove("show");
  }
});