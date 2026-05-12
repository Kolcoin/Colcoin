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

/* ===== Отправка форм через FormSubmit AJAX (без бэкенда) ===== */
const FORMSUBMIT_EMAIL = 'direkt.ritual@yandex.ru'; // куда летят заявки

function submitCallback(e) {
  e.preventDefault();
  const form = e.target;
  // honeypot — отсекает ботов
  if ((form._honey && form._honey.value) || (form.company && form.company.value)) return false;

  const ok  = form.querySelector('.callback__ok');
  const err = form.querySelector('.callback__err');
  const btn = form.querySelector('button[type="submit"]');
  if (btn) { btn.disabled = true; btn.dataset.txt = btn.textContent; btn.textContent = 'Отправка…'; }
  if (ok)  ok.hidden = true;
  if (err) err.hidden = true;

  // Собираем понятную структуру для письма
  const payload = {
    'Имя': (form.name || form.elements.name || {}).value || '',
    'Телефон': (form.phone || form.elements.phone || {}).value || '',
    'Комментарий': (form.comment || form.elements.comment || {}).value || '',
    'Источник': (form.querySelector('input[name="Источник"]') || {}).value
                || (form.elements['Источник'] || {}).value
                || ('Страница: ' + location.href),
    'Страница': location.href,
    'UTM-метки': location.search || '—',
    '_subject': (form.querySelector('input[name="_subject"]') || {}).value
                || 'Заявка с сайта urban-ritual.ru',
    '_template': 'table',
    '_captcha': 'false'
  };

  fetch('https://formsubmit.co/ajax/' + encodeURIComponent(FORMSUBMIT_EMAIL), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(r => r.json())
  .then(d => {
    if (d && (d.success === 'true' || d.success === true)) {
      if (ok) ok.hidden = false;
      // Цель в Яндекс.Метрике
      if (typeof ym === 'function') ym(109160037, 'reachGoal', 'callback_form_submit');
      form.reset();
    } else {
      if (err) err.hidden = false;
    }
  })
  .catch(() => { if (err) err.hidden = false; })
  .finally(() => {
    if (btn) { btn.disabled = false; btn.textContent = btn.dataset.txt || 'Жду звонка'; }
  });

  return false;
}

/* Клики по телефонам — цель в Метрике */
document.addEventListener('click', function (e) {
  const a = e.target.closest('a[href^="tel:"]');
  if (a && typeof ym === 'function') ym(109160037, 'reachGoal', 'phone_click');
}, true);

/* ===== Плавающая модалка «Заказать звонок» (на всех страницах) ===== */
(function () {
  if (document.getElementById('cb-modal')) return;
  const html = `
    <button type="button" class="fab fab--cb" id="cb-open" aria-label="Заказать обратный звонок">
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
        <path fill="currentColor" d="M20 15.5c-1.25 0-2.45-.2-3.57-.57a1 1 0 0 0-1.02.24l-2.2 2.2a15.05 15.05 0 0 1-6.59-6.59l2.2-2.2a1 1 0 0 0 .25-1.02A11.36 11.36 0 0 1 8.5 4a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1c0 9.39 7.61 17 17 17a1 1 0 0 0 1-1v-3.5a1 1 0 0 0-1-1Z"/>
      </svg>
      <span>Обратный звонок</span>
    </button>
    <div class="modal" id="cb-modal" role="dialog" aria-modal="true" aria-labelledby="cb-title" hidden>
      <div class="modal__backdrop" data-close></div>
      <div class="modal__win">
        <button type="button" class="modal__close" data-close aria-label="Закрыть">×</button>
        <h3 id="cb-title">Заказать обратный звонок</h3>
        <p class="modal__sub">Перезвоним в&nbsp;течение 5&nbsp;минут, круглосуточно. Звонок бесплатный.</p>
        <form class="callback" onsubmit="return submitCallback(event)" novalidate>
          <label>
            <span>Как к вам обращаться</span>
            <input type="text" name="name" required autocomplete="name" placeholder="Имя">
          </label>
          <label>
            <span>Телефон для связи</span>
            <input type="tel" name="phone" required autocomplete="tel" placeholder="+7 ___ ___-__-__">
          </label>
          <label>
            <span>Комментарий (необязательно)</span>
            <textarea name="comment" rows="2" placeholder="Адрес, удобное время или вопрос"></textarea>
          </label>
          <input type="text" name="_honey" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true">
          <input type="hidden" name="_subject" value="Заявка с сайта urban-ritual.ru — модальная форма">
          <input type="hidden" name="Источник" value="Модальная форма (плавающая кнопка)">
          <label class="consent">
            <input type="checkbox" required checked>
            <span>Согласен с&nbsp;<a href="/#contacts">обработкой персональных данных</a></span>
          </label>
          <button type="submit" class="btn btn--primary btn--block">Жду звонка</button>
          <p class="callback__ok" hidden>Спасибо! Перезвоним в&nbsp;течение 5&nbsp;минут.</p>
          <p class="callback__err" hidden>Не&nbsp;удалось отправить. Позвоните <a href="tel:+79852198394">+7&nbsp;(985)&nbsp;219-83-94</a></p>
        </form>
      </div>
    </div>`;
  document.body.insertAdjacentHTML('beforeend', html);

  const modal = document.getElementById('cb-modal');
  const open  = document.getElementById('cb-open');
  function show() { modal.hidden = false; setTimeout(() => modal.querySelector('input[name=name]').focus(), 50); }
  function hide() { modal.hidden = true; }
  open.addEventListener('click', show);
  modal.addEventListener('click', e => { if (e.target.hasAttribute('data-close')) hide(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !modal.hidden) hide(); });

  // После успешной отправки — закрыть модалку через 3 сек
  modal.addEventListener('animationend', () => {});
  modal.querySelector('form').addEventListener('submit', () => {
    setTimeout(() => {
      const ok = modal.querySelector('.callback__ok');
      if (ok && !ok.hidden) setTimeout(hide, 3000);
    }, 600);
  });
})();

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
