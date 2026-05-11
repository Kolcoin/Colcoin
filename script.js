// Минимальный JS: маска телефона + обработка формы (демо без бэка).

(function () {
  const tel = document.querySelector('input[type="tel"]');
  if (tel) {
    tel.addEventListener('input', function () {
      let d = this.value.replace(/\D/g, '');
      if (d.startsWith('8')) d = '7' + d.slice(1);
      if (!d.startsWith('7')) d = '7' + d;
      d = d.slice(0, 11);
      const p = ['+7'];
      if (d.length > 1) p.push(' (' + d.slice(1, 4));
      if (d.length >= 4) p[1] += ')';
      if (d.length >= 5) p.push(' ' + d.slice(4, 7));
      if (d.length >= 8) p.push('-' + d.slice(7, 9));
      if (d.length >= 10) p.push('-' + d.slice(9, 11));
      this.value = p.join('');
    });
  }
})();

function submitCallback(e) {
  e.preventDefault();
  const form = e.target;
  // honeypot
  if (form.company && form.company.value) return false;
  const ok = form.querySelector('.callback__ok');
  if (ok) {
    ok.hidden = false;
    form.querySelector('button[type="submit"]').disabled = true;
  }
  // В реальном проекте сюда идёт fetch на бэкенд / Telegram-бот / CRM.
  return false;
}
