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

/* ===== City switcher dropdown ===== */
(function () {
  const switcher = document.querySelector('[data-city-switcher]');
  if (!switcher || !window.CITIES_MO) return;
  const btn = switcher.querySelector('.city-switcher__btn');
  const pop = switcher.querySelector('.city-switcher__pop');
  const list = switcher.querySelector('.city-switcher__list');
  const input = switcher.querySelector('.city-switcher__input');

  // Build list
  function render(q) {
    q = (q || '').toLowerCase().trim();
    const base = location.pathname.indexOf('/city/') > -1 ? '../' : 'city/';
    const items = window.CITIES_MO
      .filter(c => !q || c.name.toLowerCase().includes(q))
      .map(c => `<li><a href="${base}${c.slug}/">${c.name}</a></li>`)
      .join('');
    list.innerHTML = items || '<li class="empty">Ничего не найдено</li>';
  }
  render('');

  btn.addEventListener('click', () => {
    const open = !pop.hidden;
    pop.hidden = open;
    btn.setAttribute('aria-expanded', String(!open));
    if (!open) setTimeout(() => input.focus(), 50);
  });
  input.addEventListener('input', () => render(input.value));
  document.addEventListener('click', (e) => {
    if (!switcher.contains(e.target)) {
      pop.hidden = true;
      btn.setAttribute('aria-expanded', 'false');
    }
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      pop.hidden = true;
      btn.setAttribute('aria-expanded', 'false');
    }
  });
})();

/* ===== Cities grid on the main page ===== */
(function () {
  const grid = document.getElementById('cities-grid');
  const filter = document.getElementById('cities-filter-input');
  if (!grid || !window.CITIES_MO) return;

  const base = location.pathname.indexOf('/city/') > -1 ? '../' : 'city/';

  function render(q) {
    q = (q || '').toLowerCase().trim();
    const html = window.CITIES_MO
      .filter(c => !q || c.name.toLowerCase().includes(q))
      .map(c => `<li><a href="${base}${c.slug}/"><span class="cgrid__name">${c.name}</span><span class="cgrid__min">от ${c.minutes} мин</span></a></li>`)
      .join('');
    grid.innerHTML = html || '<li class="empty">Город не найден. Звоните — обсудим выезд.</li>';
  }
  render('');
  if (filter) filter.addEventListener('input', () => render(filter.value));
})();
