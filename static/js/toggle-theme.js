import { postAction } from './utils.js'

const themeToggleBtnElement = document.getElementById("themeToggleBtn")
const themeIconElement = themeToggleBtnElement.querySelector("i")
const bodyElement = document.body

themeToggleBtnElement.addEventListener("click", async () => {
  const data = await postAction(bodyElement.dataset.themeToggleUrl)

  if (data.new_theme === 'dark') {
    themeIconElement.classList.replace("bi-sun-fill", 'bi-moon-stars-fill')
    bodyElement.setAttribute('data-bs-theme', 'dark')
  } else {
    themeIconElement.classList.replace('bi-moon-stars-fill', "bi-sun-fill")
    bodyElement.setAttribute('data-bs-theme', 'light')
  }
})