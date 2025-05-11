document.addEventListener('DOMContentLoaded', function() {
    const burgerButton = document.getElementById('burger');
    const mobileMenu = document.getElementById('mobile-menu');
    let isMenuOpen = false;
    
    // Функция для открытия/закрытия меню
    function toggleMenu() {
      isMenuOpen = !isMenuOpen;
      
      if (isMenuOpen) {
        mobileMenu.style.display = 'block';
        mobileMenu.style.animation = 'slideDown 0.3s forwards';
        burgerButton.querySelector('.material-symbols-outlined').textContent = 'close';
      } else {
        mobileMenu.style.animation = '';
        mobileMenu.style.display = 'none';
        burgerButton.querySelector('.material-symbols-outlined').textContent = 'menu';
      }
    }
    
    // Обработчик клика по бургер-кнопке
    if (burgerButton && mobileMenu) {
      burgerButton.addEventListener('click', toggleMenu);
      
      // Закрытие меню при клике на пункт меню
      const menuLinks = mobileMenu.querySelectorAll('a');
      menuLinks.forEach(link => {
        link.addEventListener('click', toggleMenu);
      });
    }
    
    // Закрытие меню при изменении размера окна
    window.addEventListener('resize', function() {
      if (window.innerWidth > 768 && isMenuOpen) {
        mobileMenu.style.display = 'none';
        isMenuOpen = false;
        if (burgerButton) {
          burgerButton.querySelector('.material-symbols-outlined').textContent = 'menu';
        }
      }
    });
  });