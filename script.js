const phoneInput = document.querySelector("#phone");
const form = document.querySelector("#lead-form");
const message = document.querySelector(".form-message");
const filterButtons = document.querySelectorAll("#materialFilters .filter-btn");
const monumentCards = document.querySelectorAll("#monuments .card");

if (filterButtons.length && monumentCards.length) {
  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const selected = button.dataset.filter;

      filterButtons.forEach((item) => item.classList.remove("active"));
      button.classList.add("active");

      monumentCards.forEach((card) => {
        const material = card.dataset.material;
        const shouldShow = selected === "all" || material === selected;
        card.style.display = shouldShow ? "grid" : "none";
      });
    });
  });
}

if (phoneInput) {
  phoneInput.addEventListener("input", () => {
    const digits = phoneInput.value.replace(/\D/g, "");
    const trimmed = digits.slice(0, 11);
    let formatted = "+7";

    if (trimmed.length > 1) {
      formatted += " (" + trimmed.slice(1, 4);
    }
    if (trimmed.length >= 4) {
      formatted += ") " + trimmed.slice(4, 7);
    }
    if (trimmed.length >= 7) {
      formatted += "-" + trimmed.slice(7, 9);
    }
    if (trimmed.length >= 9) {
      formatted += "-" + trimmed.slice(9, 11);
    }

    phoneInput.value = formatted;
  });
}

if (form && message) {
  form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!form.checkValidity()) {
      message.textContent = "Проверьте корректность заполнения формы.";
      message.classList.remove("ok");
      message.classList.add("error");
      return;
    }

    message.textContent =
      "Спасибо! Заявка принята. Менеджер свяжется с вами в ближайшее время.";
    message.classList.remove("error");
    message.classList.add("ok");
    form.reset();
  });
}
