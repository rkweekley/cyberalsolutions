// Inject shared partials into placeholders marked with data-include.
(function () {
  'use strict';

  function toArray(list) {
    return Array.prototype.slice.call(list || []);
  }

  function executeScripts(root) {
    toArray(root.querySelectorAll('script')).forEach(function (script) {
      var replacement = document.createElement('script');
      toArray(script.attributes).forEach(function (attr) {
        replacement.setAttribute(attr.name, attr.value);
      });
      replacement.text = script.text;
      script.parentNode.replaceChild(replacement, script);
    });
  }

  function replaceTargetWithHtml(target, html) {
    var parent = target.parentNode;
    if (!parent) return;
    var wrapper = document.createElement('div');
    wrapper.innerHTML = html;
    parent.insertBefore(wrapper, target);
    parent.removeChild(target);
    executeScripts(wrapper);
    while (wrapper.firstChild) {
      parent.insertBefore(wrapper.firstChild, wrapper);
    }
    parent.removeChild(wrapper);
  }

  function loadPartial(target) {
    var url = target.getAttribute('data-include');
    if (!url) return Promise.resolve();
    return fetch(url, { credentials: 'same-origin', cache: 'no-store' })
      .then(function (response) {
        if (!response.ok) throw new Error('Failed to load ' + url);
        return response.text();
      })
      .then(function (html) {
        if (!html) return;
        replaceTargetWithHtml(target, html);
      })
      .catch(function (err) {
        console.error(err);
      });
  }

  function init() {
    var targets = toArray(document.querySelectorAll('[data-include]'));
    if (!targets.length) return;
    Promise.all(targets.map(loadPartial));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
