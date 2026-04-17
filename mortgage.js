function formatCurrency(amount) {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0
  }).format(amount);
}

function annuityPayment(loan, annualRate, years) {
  const months = years * 12;
  const monthlyRate = annualRate / 100 / 12;
  if (monthlyRate === 0) return loan / months;
  return (loan * monthlyRate) / (1 - (1 + monthlyRate) ** -months);
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

  resultEl.innerHTML = `
    <div class="mortgage-result-grid">
      <article class="project-card">
        <h3>Сумма кредита</h3>
        <p class="project-price">${formatCurrency(loan)}</p>
      </article>
      <article class="project-card">
        <h3>Ежемесячный платёж</h3>
        <p class="project-price">${formatCurrency(monthly)}</p>
      </article>
      <article class="project-card">
        <h3>Переплата</h3>
        <p class="project-price">${formatCurrency(overpayment)}</p>
      </article>
      <article class="project-card">
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
