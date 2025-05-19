document.addEventListener("DOMContentLoaded", () => {
  // Находим все меню пользователя
  const userMenus = document.querySelectorAll(".user-menu")

  userMenus.forEach((menu) => {
    const button = menu.querySelector(".user-menu-button")
    const dropdown = menu.querySelector(".dropdown-menu")

    if (!button || !dropdown) return

    // Флаг состояния меню
    let isOpen = false

    // Функция для открытия/закрытия меню
    function toggleMenu(event) {
      if (event) {
        event.preventDefault()
        event.stopPropagation()
      }

      isOpen = !isOpen

      if (isOpen) {
        dropdown.style.display = "block"
      } else {
        dropdown.style.display = "none"
      }
    }

    // Обработчик клика на кнопку
    button.addEventListener("click", toggleMenu)

    // Закрытие меню при клике на пункт меню
    const menuItems = dropdown.querySelectorAll(".dropdown-item")
    menuItems.forEach((item) => {
      item.addEventListener("click", () => {
        if (isOpen) {
          toggleMenu()
        }
      })
    })

    // Закрытие меню при клике вне меню
    document.addEventListener("click", (event) => {
      if (isOpen && !dropdown.contains(event.target) && event.target !== button && !button.contains(event.target)) {
        toggleMenu()
      }
    })
  })
})
