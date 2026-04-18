function formatCurrency(amount) {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0
  }).format(amount);
}

function svgToDataUri(svg) {
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

function getMortgageVisuals() {
  return {
    loan: svgToDataUri(`
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 220" role="img" aria-label="Сумма кредита">
        <rect width="640" height="220" fill="#f2f4f9"/>
        <rect x="56" y="56" width="528" height="108" rx="16" fill="#e8ecf5"/>
        <rect x="84" y="84" width="156" height="20" rx="10" fill="#9aa4b8"/>
        <rect x="84" y="116" width="200" height="20" rx="10" fill="#808ca3"/>
        <rect x="432" y="82" width="112" height="56" rx="12" fill="#dde3ee" stroke="#8a95aa" stroke-width="4"/>
        <path d="M452 110h72" stroke="#8a95aa" stroke-width="6" stroke-linecap="round"/>
      </svg>
    `),
    monthly: svgToDataUri(`
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 220" role="img" aria-label="Ежемесячный платеж">
        <rect width="640" height="220" fill="#f2f4f9"/>
        <rect x="70" y="62" width="500" height="98" rx="18" fill="#e8ecf5"/>
        <circle cx="138" cy="112" r="32" fill="#d7deea" stroke="#8a95aa" stroke-width="4"/>
        <path d="M138 95v20l14 10" stroke="#7f8ba1" stroke-width="6" stroke-linecap="round" fill="none"/>
        <rect x="206" y="92" width="136" height="14" rx="7" fill="#95a0b5"/>
        <rect x="206" y="118" width="202" height="14" rx="7" fill="#7f8ba1"/>
      </svg>
    `),
    overpayment: svgToDataUri(`
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 220" role="img" aria-label="Переплата">
        <rect width="640" height="220" fill="#f2f4f9"/>
        <rect x="84" y="140" width="70" height="34" rx="8" fill="#cfd7e5"/>
        <rect x="174" y="122" width="70" height="52" rx="8" fill="#bfc9da"/>
        <rect x="264" y="104" width="70" height="70" rx="8" fill="#adb9cf"/>
        <rect x="354" y="86" width="70" height="88" rx="8" fill="#9eabc4"/>
        <path d="M96 82l72 14 62-22 58 24 62-32 76 22" stroke="#7f8ba1" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `),
    rate: svgToDataUri(`
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 220" role="img" aria-label="Ставка">
        <rect width="640" height="220" fill="#f2f4f9"/>
        <circle cx="210" cy="110" r="56" fill="#dce2ed"/>
        <circle cx="210" cy="110" r="34" fill="#f2f4f9"/>
        <path d="M320 78h214M320 110h180M320 142h132" stroke="#8b97ad" stroke-width="10" stroke-linecap="round"/>
        <path d="M198 74h22c18 0 28 8 28 21 0 12-8 20-24 23l-20 3c-10 2-14 5-14 11 0 8 6 13 17 13h41" fill="none" stroke="#77859f" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `)
  };
}

function annuityPayment(loan, annualRate, years) {
  const months = years * 12;
  const monthlyRate = annualRate / 100 / 12;
  if (monthlyRate === 0) return loan / months;
  return (loan * monthlyRate) / (1 - (1 + monthlyRate) ** -months);
}

function reachMetrikaGoal(goal, params = {}) {
  try {
    if (typeof window !== "undefined" && typeof window.ym === "function") {
      window.ym(108657608, "reachGoal", goal, params);
    }
  } catch (_error) {
    // no-op in browsers where metrika is unavailable
  }
}

function recalcMortgage() {
  const propertyPriceInput = document.getElementById("mortgage-price");
  const downPaymentInput = document.getElementById("mortgage-down-payment");
  const yearsInput = document.getElementById("mortgage-years");
  const rateInput = document.getElementById("mortgage-rate");
  const resultEl = document.getElementById("mortgage-result-cards");
  const errorEl = document.getElementById("mortgage-result-error");
  if (!propertyPriceInput || !downPaymentInput || !yearsInput || !rateInput || !resultEl) return;

  const propertyPrice = Number(propertyPriceInput.value) || 0;
  const downPayment = Number(downPaymentInput.value) || 0;
  const years = Number(yearsInput.value) || 0;
  const annualRate = Number(rateInput.value) || 0;

  const loan = propertyPrice - downPayment;
  if (loan <= 0 || years <= 0 || annualRate < 0) {
    resultEl.innerHTML = "";
    if (errorEl) {
      errorEl.textContent =
        "Проверьте параметры: стоимость должна быть больше взноса, срок — больше 0, ставка — неотрицательная.";
    }
    return;
  }

  if (errorEl) errorEl.textContent = "";
  const monthly = annuityPayment(loan, annualRate, years);
  const months = years * 12;
  const totalPaid = monthly * months;
  const overpayment = Math.max(totalPaid - loan, 0);
  const visuals = getMortgageVisuals();

  resultEl.innerHTML = `
    <div class="mortgage-result-grid">
      <article class="project-card mortgage-result-card">
        <figure class="mortgage-result-media">
          <img class="mortgage-result-image" src="${visuals.loan}" alt="" loading="lazy" />
        </figure>
        <h3>Сумма кредита</h3>
        <p class="project-price">${formatCurrency(loan)}</p>
      </article>
      <article class="project-card mortgage-result-card">
        <figure class="mortgage-result-media">
          <img class="mortgage-result-image" src="${visuals.monthly}" alt="" loading="lazy" />
        </figure>
        <h3>Ежемесячный платёж</h3>
        <p class="project-price">${formatCurrency(monthly)}</p>
      </article>
      <article class="project-card mortgage-result-card">
        <figure class="mortgage-result-media">
          <img class="mortgage-result-image" src="${visuals.overpayment}" alt="" loading="lazy" />
        </figure>
        <h3>Переплата</h3>
        <p class="project-price">${formatCurrency(overpayment)}</p>
      </article>
      <article class="project-card mortgage-result-card">
        <figure class="mortgage-result-media">
          <img class="mortgage-result-image" src="${visuals.rate}" alt="" loading="lazy" />
        </figure>
        <h3>Ставка</h3>
        <p class="project-price">${annualRate.toFixed(2)}%</p>
      </article>
    </div>
  `;
}

function initMortgageFaqAccordion() {
  document.querySelectorAll("#mortgage-faq .faq-accordion-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", expanded ? "false" : "true");
      const panel = button.nextElementSibling;
      if (panel) panel.hidden = expanded;
    });
  });
}

function initMortgagePage() {
  const rateInput = document.getElementById("mortgage-rate");
  const programSelect = document.getElementById("mortgage-program");
  const priceInput = document.getElementById("mortgage-price");
  const downPaymentInput = document.getElementById("mortgage-down-payment");
  const yearsInput = document.getElementById("mortgage-years");
  const form = document.getElementById("mortgage-form");

  if (programSelect && rateInput) {
    programSelect.innerHTML = window.REALTY_MORTGAGE_PROGRAMS
      .map(
        (program) => `
        <option value="${program.id}">${program.title} · ${program.rate.toFixed(2)}%</option>
      `
      )
      .join("");
    const firstProgram = window.REALTY_MORTGAGE_PROGRAMS[0];
    if (firstProgram) {
      rateInput.value = String(firstProgram.rate);
    }
  }

  const tableBody = document.getElementById("mortgage-programs-table");
  if (tableBody) {
    tableBody.innerHTML = window.REALTY_MORTGAGE_PROGRAMS
      .map(
        (program) => `
        <tr>
          <td>${program.title}</td>
          <td>${program.rate.toFixed(2)}%</td>
          <td>${program.minDownPayment}%</td>
          <td>до ${program.maxAmountMln} млн ₽</td>
          <td>${program.termYears} лет</td>
        </tr>
      `
      )
      .join("");
  }

  const faqRoot = document.getElementById("mortgage-faq");
  if (faqRoot) {
    faqRoot.innerHTML = (window.REALTY_MORTGAGE_FAQ || [])
      .map(
        (item, idx) => `
      <article class="faq-item">
        <button class="faq-accordion-btn" type="button" aria-expanded="false" data-faq="${idx}">
          ${item.q}
        </button>
        <div class="faq-accordion-panel" hidden>
          <p>${item.a}</p>
        </div>
      </article>
    `
      )
      .join("");
  }

  form?.addEventListener("submit", (event) => {
    event.preventDefault();
    reachMetrikaGoal("lead_submit", { source: "mortgage_form" });
    reachMetrikaGoal("mortgage_calc");
    recalcMortgage();
  });
  programSelect?.addEventListener("change", () => {
    const selected = window.REALTY_MORTGAGE_PROGRAMS.find((program) => program.id === programSelect.value);
    if (selected && rateInput) {
      rateInput.value = String(selected.rate);
      recalcMortgage();
    }
  });
  [priceInput, downPaymentInput, yearsInput, rateInput].forEach((input) => {
    input?.addEventListener("input", recalcMortgage);
  });

  initMortgageFaqAccordion();
  recalcMortgage();
}

initMortgagePage();
