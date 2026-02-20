// Toggle mobile menu aria-expanded and body data attribute for open state
(function () {
  'use strict';

  function toggleBodyAttribute(name) {
    if (document.body.toggleAttribute) {
      document.body.toggleAttribute(name);
      return;
    }

    if (document.body.hasAttribute(name)) {
      document.body.removeAttribute(name);
    } else {
      document.body.setAttribute(name, '');
    }
  }

  function init() {
    var btns = document.querySelectorAll('#mobile-menu');
    Array.prototype.slice.call(btns).forEach(function (btn) {
      btn.addEventListener('click', function () {
        var expanded = this.getAttribute('aria-expanded') === 'true';
        this.setAttribute('aria-expanded', String(!expanded));
        toggleBodyAttribute('data-mobile-menu-open');
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
