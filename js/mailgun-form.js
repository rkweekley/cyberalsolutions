(function () {
  // Village API contact endpoint — sends via Mailgun to info@cyberalsolutions.com.
  var ENDPOINT = 'https://api.villagefamily.app/api/auth/contact';

  var forms = document.querySelectorAll('form[data-mailgun-form]');
  if (!forms.length) return;

  function wire(form) {
    var status = form.querySelector('.form-status');
    var btn = form.querySelector('button[type=submit]');
    var subjectPrefix = form.getAttribute('data-subject') || 'Website form';
    var gaEvent = form.getAttribute('data-ga-event') || 'form_submit';

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      // Honeypot: bots fill hidden field -> fake success, submit nothing.
      if (form.elements.company_website && form.elements.company_website.value !== '') {
        status.textContent = 'Thanks! Your message is on its way. We\u2019ll reply within one business day.';
        status.className = 'form-status text-center mt-4 ok';
        form.reset();
        return;
      }
      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }
      btn.disabled = true;
      btn.textContent = 'Sending\u2026';
      status.textContent = '';

      // Required fields for the endpoint: name, email, subject, message.
      // Any EXTRA labeled fields (org, device count, ...) get folded into the message.
      var name = form.elements.name.value.trim();
      var email = form.elements.email.value.trim();
      var extras = [];
      var core = { name: 1, email: 1, message: 1, company_website: 1 };
      Array.prototype.forEach.call(form.elements, function (el) {
        if (!el.name || core[el.name] || el.type === 'submit') return;
        if (el.type === 'checkbox' || el.type === 'radio') return;
        if (!el.value.trim()) return;
        var label = (form.querySelector('label[for="' + el.id + '"]') || {}).textContent || el.name;
        extras.push(label.replace(/\s+/g, ' ').trim() + ': ' + el.value.trim());
      });

      var message = (form.elements.message ? form.elements.message.value.trim() : '');
      if (extras.length) message = extras.join('\n') + (message ? '\n\n' + message : '');
      if (!message) message = '(no message given)';

      fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name,
          email: email,
          subject: subjectPrefix + ': ' + name,
          message: message + '\n\n-- Sent from cyberalsolutions.com' + location.pathname
        })
      })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, body: j }; }); })
        .then(function (res) {
          if (!res.ok) throw new Error(res.body.error || 'HTTP error');
          status.textContent = 'Thanks! Your message is on its way. We\u2019ll reply within one business day.';
          status.className = 'form-status text-center mt-4 ok';
          form.reset();
          if (window.gtag) gtag('event', gaEvent, { event_category: 'lead' });
        })
        .catch(function () {
          status.textContent = 'Hmm, that didn\u2019t go through. Call or text (740) 315-8211, or email info@cyberalsolutions.com and we\u2019ll pick it up there.';
          status.className = 'form-status text-center mt-4 err';
          if (window.gtag) gtag('event', gaEvent + '_error', { event_category: 'lead' });
        })
        .finally(function () { btn.disabled = false; btn.textContent = btn.getAttribute('data-label') || 'Send'; });
    });
  }

  Array.prototype.forEach.call(forms, wire);
})();
