// Basic site initialization for lazy loading and preloader cleanup.
(function () {
  'use strict';

  function init() {
    var preloader = document.querySelector('.preloader');
    if (preloader) {
      preloader.style.opacity = '0';
      preloader.style.pointerEvents = 'none';
      preloader.style.transition = 'opacity 120ms ease';
      window.setTimeout(function () {
        preloader.style.display = 'none';
      }, 150);
    }

    if (window.lozad) {
      window.lozad().observe();
    }
  }

  if (document.readyState === 'complete') {
    init();
  } else {
    window.addEventListener('load', init, { once: true });
  }
})();
