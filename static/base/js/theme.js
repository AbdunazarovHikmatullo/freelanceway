document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("theme-toggle")
  const themeIcon = themeToggle.querySelector(".material-symbols-outlined")

  // Функция для установки темы
  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme)
    localStorage.setItem("theme", theme)

    // Обновляем иконку
    themeIcon.textContent = theme === "dark" ? "light_mode" : "dark_mode"
  }

  // Получаем сохраненную тему или используем системные настройки
  const savedTheme = localStorage.getItem("theme")
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches

  if (savedTheme) {
    setTheme(savedTheme)
  } else {
    setTheme(prefersDark ? "dark" : "light")
  }

  // Обработчик переключения темы
  themeToggle.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme")
    const newTheme = currentTheme === "dark" ? "light" : "dark"
    setTheme(newTheme)
  })
})
