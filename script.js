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

/* ===== Отправка форм через FormSubmit AJAX (без бэкенда) =====
   Используется активированный хеш FormSubmit вместо «голого» email.
   Преимущества: (1) не нужна повторная активация формы при изменениях,
   (2) email не виден спам-ботам, (3) Cloudflare-защита FormSubmit лояльнее
   относится к запросам с хешем, чем с email.
   Активирован для direkt.ritual@yandex.ru (письмо «Action Required: Activate FormSubmit»). */
const FORMSUBMIT_EMAIL = 'f2f92f8ed5ed154d0e712899e0d490e5'; // → direkt.ritual@yandex.ru

/* Конфиг каналов доставки заявок. Срабатывает по приоритету (1-й, 2-й…).
   Если первый канал упал — пробуем следующий. Если все упали — показываем кнопки
   мессенджеров с pre-filled текстом, чтобы пользователь точно мог нас достать. */
const WHATSAPP_NUMBER = '79852198394';            // без +
const TELEGRAM_USERNAME = 'ritual_khimki';        // без @

function fmtPayloadText(p) {
  return [
    '🔔 Заявка с сайта urban-ritual.ru',
    '',
    'Имя: ' + (p['Имя'] || '—'),
    'Телефон: ' + (p['Телефон'] || '—'),
    'Комментарий: ' + (p['Комментарий'] || '—'),
    '',
    'Источник: ' + (p['Источник'] || '—'),
    'Страница: ' + (p['Страница'] || location.href),
    'UTM: ' + (p['UTM-метки'] || '—'),
  ].join('\n');
}

function buildMessengerLinks(payload) {
  const text = fmtPayloadText(payload);
  const enc = encodeURIComponent(text);
  return {
    whatsapp: 'https://wa.me/' + WHATSAPP_NUMBER + '?text=' + enc,
    telegram: 'https://t.me/' + TELEGRAM_USERNAME + '?text=' + enc,
  };
}

function showFallbackUI(form, payload) {
  // Скрываем ok/err стандартные, рисуем красивый блок с кнопками мессенджеров
  const ok  = form.querySelector('.callback__ok');
  const err = form.querySelector('.callback__err');
  if (ok)  ok.hidden = true;
  if (err) err.hidden = true;

  let fallback = form.querySelector('.callback__fallback');
  if (!fallback) {
    fallback = document.createElement('div');
    fallback.className = 'callback__fallback';
    fallback.style.cssText = 'margin-top:14px;padding:14px;background:#FFF8F0;border:1px solid #E8C28A;border-radius:10px;color:#5a4520;font-size:14px;line-height:1.45';
    form.appendChild(fallback);
  }
  const links = buildMessengerLinks(payload);
  fallback.innerHTML =
    '<b>Минутку — форма временно недоступна.</b><br>' +
    'Чтобы мы точно получили заявку, выберите удобный способ:<br>' +
    '<div style="display:flex;flex-direction:column;gap:8px;margin-top:12px">' +
      '<a href="' + links.whatsapp + '" target="_blank" rel="noopener" ' +
        'onclick="if(typeof ym===\'function\')ym(109160037,\'reachGoal\',\'whatsapp_fallback\')" ' +
        'style="display:flex;align-items:center;justify-content:center;gap:8px;padding:12px 14px;background:#25D366;color:#fff;text-decoration:none;border-radius:8px;font-weight:600">' +
        '🟢 Отправить в WhatsApp (рекомендуем)</a>' +
      '<a href="tel:+79852198394" ' +
        'onclick="if(typeof ym===\'function\')ym(109160037,\'reachGoal\',\'phone_fallback\')" ' +
        'style="display:flex;align-items:center;justify-content:center;gap:8px;padding:12px 14px;background:#6E2A2A;color:#fff;text-decoration:none;border-radius:8px;font-weight:600">' +
        '📞 Позвонить +7 (985) 219-83-94</a>' +
    '</div>' +
    '<p style="margin:10px 0 0;font-size:12px;color:#7a7066">Звонок и&nbsp;ответ в&nbsp;WhatsApp&nbsp;— в&nbsp;течение 1–5&nbsp;минут, круглосуточно.</p>';
}

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
  const oldFallback = form.querySelector('.callback__fallback');
  if (oldFallback) oldFallback.remove();

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

  function onSuccess() {
    if (ok) ok.hidden = false;
    if (typeof ym === 'function') ym(109160037, 'reachGoal', 'callback_form_submit');
    if (window.URTrack && typeof window.URTrack.formSubmit === 'function') {
      window.URTrack.formSubmit();
    }
    form.reset();
  }

  function onFail() {
    // Не показываем "сухое" сообщение об ошибке — даём пользователю реальные варианты связи
    showFallbackUI(form, payload);
    // Метрика: отметим что форма упала и пользователю показан fallback
    if (typeof ym === 'function') ym(109160037, 'reachGoal', 'callback_form_fail');
  }

  function tryFormSubmit() {
    // 8-секундный таймаут чтобы пользователь долго не ждал зависшего FormSubmit
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), 8000);
    return fetch('https://formsubmit.co/ajax/' + encodeURIComponent(FORMSUBMIT_EMAIL), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(payload),
      signal: ac.signal,
      mode: 'cors'
    }).then(r => {
      clearTimeout(timer);
      if (!r.ok) throw new Error('http ' + r.status);
      return r.json();
    }).then(d => {
      if (d && (d.success === 'true' || d.success === true)) return true;
      throw new Error('formsubmit-not-success');
    });
  }

  // 1) Пробуем основной канал FormSubmit. Если упал — fallback к мессенджерам.
  tryFormSubmit()
    .then(onSuccess)
    .catch(onFail)
    .finally(() => {
      if (btn) { btn.disabled = false; btn.textContent = btn.dataset.txt || 'Жду звонка'; }
    });

  return false;
}

/* ===== Расширенный трекинг для Директа =====
   - Автоопределение города из URL вида /city/{slug}/{intent?}/
   - Goals в Метрике с city-параметром
   - Параметры визита (Метрика) для сегментации по UTM-меткам и городу
*/
(function () {
  const METRIKA_ID = 109160037;

  // 1) Автоопределение «города и интента» по URL
  function getPageContext() {
    const m = location.pathname.match(/^\/city\/([^\/]+)\/?(?:([^\/]+)\/?)?/);
    const city = m ? m[1] : null;
    const intent = m && m[2] ? m[2] : null;
    return { city, intent };
  }

  // 2) Прокидываем UTM-метки в Метрику + city как «параметры визита»
  function sendVisitParams() {
    if (typeof ym !== 'function') return;
    const ctx = getPageContext();
    const usp = new URLSearchParams(location.search);
    const params = {};
    if (ctx.city) params.city = ctx.city;
    if (ctx.intent) params.intent = ctx.intent;
    if (usp.get('utm_source'))   params.utm_source   = usp.get('utm_source');
    if (usp.get('utm_medium'))   params.utm_medium   = usp.get('utm_medium');
    if (usp.get('utm_campaign')) params.utm_campaign = usp.get('utm_campaign');
    if (usp.get('utm_content'))  params.utm_content  = usp.get('utm_content');
    if (usp.get('utm_term'))     params.utm_term     = usp.get('utm_term');
    if (Object.keys(params).length) {
      try { ym(METRIKA_ID, 'params', params); } catch (e) {}
    }
  }
  // отправка при первой загрузке + при изменении hash/history
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', sendVisitParams);
  } else {
    sendVisitParams();
  }

  // 3) Универсальный трекинг кликов по контактам и формам
  function reachGoal(name) {
    if (typeof ym !== 'function') return;
    try { ym(METRIKA_ID, 'reachGoal', name); } catch (e) {}
  }

  document.addEventListener('click', function (e) {
    const a = e.target.closest('a[href]');
    if (!a) return;
    const href = (a.getAttribute('href') || '').toLowerCase();
    const ctx = getPageContext();
    const suffix = ctx.city ? '_' + ctx.city : '';
    const intentSuffix = ctx.intent ? '_' + ctx.intent : '';

    // --- Telephone clicks ---
    if (href.startsWith('tel:')) {
      reachGoal('phone_click');                   // общая
      if (ctx.city) {
        reachGoal('phone_click' + suffix);        // напр. phone_click_mytishchi
        if (ctx.intent) reachGoal('phone_click' + suffix + intentSuffix); // phone_click_mytishchi_kremaciya
      }
      return;
    }

    // --- WhatsApp ---
    if (href.indexOf('wa.me') > -1 || href.indexOf('whatsapp') > -1) {
      reachGoal('whatsapp_click');
      if (ctx.city) reachGoal('whatsapp_click' + suffix);
      return;
    }

    // --- Telegram ---
    if (href.indexOf('t.me') > -1 || href.indexOf('telegram') > -1) {
      reachGoal('telegram_click');
      if (ctx.city) reachGoal('telegram_click' + suffix);
      return;
    }

    // --- Email ---
    if (href.startsWith('mailto:')) {
      reachGoal('email_click');
      if (ctx.city) reachGoal('email_click' + suffix);
      return;
    }
  }, true);

  // 4) Удобный глобал-helper для всех форм: вызовем из submitCallback() и других мест
  window.URTrack = {
    formSubmit: function () {
      reachGoal('form_submit');
      const ctx = getPageContext();
      const suffix = ctx.city ? '_' + ctx.city : '';
      if (ctx.city) reachGoal('form_submit' + suffix);
    },
    context: getPageContext
  };
})();

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
