document.addEventListener("DOMContentLoaded", () => {
  // Получаем элементы
  const menuToggle = document.getElementById("mobile-menu-toggle")
  const mobileMenu = document.getElementById("mobile-menu")

  // Проверяем, существуют ли элементы
  if (!menuToggle || !mobileMenu) {
    console.error("Элементы мобильного меню не найдены")
    return
  }

  // Флаг состояния меню
  let isMenuOpen = false

  // Функция для открытия/закрытия меню
  function toggleMenu(event) {
    // Предотвращаем стандартное поведение и всплытие события
    if (event) {
      event.preventDefault()
      event.stopPropagation()
    }

    // Переключаем состояние
    isMenuOpen = !isMenuOpen

    // Применяем изменения
    if (isMenuOpen) {
      mobileMenu.style.display = "block"
      menuToggle.querySelector(".material-symbols-outlined").textContent = "close"
      document.body.style.overflow = "hidden" // Блокируем прокрутку
    } else {
      mobileMenu.style.display = "none"
      menuToggle.querySelector(".material-symbols-outlined").textContent = "menu"
      document.body.style.overflow = "" // Разблокируем прокрутку
    }
  }

  // Обработчик клика на кнопку меню
  menuToggle.addEventListener("click", toggleMenu)

  // Закрытие меню при клике на пункт меню
  const menuLinks = mobileMenu.querySelectorAll("a")
  menuLinks.forEach((link) => {
    link.addEventListener("click", () => {
      if (isMenuOpen) {
        toggleMenu()
      }
    })
  })

  // Закрытие меню при клике вне меню
  document.addEventListener("click", (event) => {
    if (
      isMenuOpen &&
      !mobileMenu.contains(event.target) &&
      event.target !== menuToggle &&
      !menuToggle.contains(event.target)
    ) {
      toggleMenu()
    }
  })

  // Закрытие меню при изменении размера окна
  window.addEventListener("resize", () => {
    if (window.innerWidth > 768 && isMenuOpen) {
      toggleMenu()
    }
  })
})
