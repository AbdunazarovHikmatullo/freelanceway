document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar")
  const toggleSidebarBtn = document.getElementById("toggle-sidebar")
  const closeSidebarBtn = document.getElementById("close-sidebar")
  const body = document.body

  // Функция для открытия/закрытия боковой панели на мобильных устройствах
  function toggleSidebar() {
    if (window.innerWidth <= 1024) {
      sidebar.classList.toggle("sidebar-visible")
    } else {
      body.classList.toggle("sidebar-collapsed")
      sidebar.classList.toggle("sidebar-collapsed")
    }
  }

  // Функция для закрытия боковой панели на мобильных устройствах
  function closeSidebar() {
    if (window.innerWidth <= 1024) {
      sidebar.classList.remove("sidebar-visible")
    }
  }

  // Обработчики событий
  if (toggleSidebarBtn) {
    toggleSidebarBtn.addEventListener("click", toggleSidebar)
  }

  if (closeSidebarBtn) {
    closeSidebarBtn.addEventListener("click", closeSidebar)
  }

  // Закрытие боковой панели при клике вне её на мобильных устройствах
  document.addEventListener("click", (event) => {
    if (
      window.innerWidth <= 1024 &&
      sidebar.classList.contains("sidebar-visible") &&
      !sidebar.contains(event.target) &&
      event.target !== toggleSidebarBtn
    ) {
      closeSidebar()
    }
  })

  // Обработка изменения размера окна
  window.addEventListener("resize", () => {
    if (window.innerWidth > 1024) {
      sidebar.classList.remove("sidebar-visible")
    }
  })

  // Обработка клика по пунктам меню на мобильных устройствах
  const sidebarLinks = sidebar.querySelectorAll("a")
  sidebarLinks.forEach((link) => {
    link.addEventListener("click", () => {
      if (window.innerWidth <= 1024) {
        closeSidebar()
      }
    })
  })
})
