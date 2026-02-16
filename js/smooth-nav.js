// Smooth-scroll home section links and redirect from subpages.
(function () {
  'use strict';

  var homePaths = ['/', '/index.html'];

  function isHomePath(path) {
    return homePaths.indexOf(path) !== -1;
  }

  function handleClick(event) {
    var link = event.currentTarget;
    if (!link || !link.href) return;

    var url;
    try {
      url = new URL(link.href, window.location.href);
    } catch (err) {
      return;
    }

    if (!url.hash) return;

    var currentPath = window.location.pathname || '/';
    var linkPath = url.pathname || '/';
    var onHome = isHomePath(currentPath);
    var linkToHome = isHomePath(linkPath);

    if (!linkToHome) return;

    if (!onHome) {
      event.preventDefault();
      window.location.href = '/index.html' + url.hash;
      return;
    }

    var target = document.querySelector(url.hash);
    if (!target) return;

    event.preventDefault();
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    target.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' });
    history.replaceState(null, '', url.hash);
  }

  function init() {
    var links = document.querySelectorAll('nav a[href*="#"], .page-scroll[href*="#"]');
    if (!links.length) return;
    Array.prototype.slice.call(links).forEach(function (link) {
      link.addEventListener('click', handleClick);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
