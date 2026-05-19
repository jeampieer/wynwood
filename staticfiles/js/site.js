document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".alert").forEach((alert) => {
    window.setTimeout(() => alert.remove(), 6000);
  });

  const promoCountdown = document.querySelector("[data-promo-countdown]");
  if (promoCountdown) {
    const duration = Number(promoCountdown.dataset.promoDurationMinutes || 1979) * 60 * 1000;
    const storageKey = `whPromoDeadline:${duration}`;
    const nodes = {
      days: promoCountdown.querySelector("[data-promo-days]"),
      hours: promoCountdown.querySelector("[data-promo-hours]"),
      minutes: promoCountdown.querySelector("[data-promo-minutes]"),
      seconds: promoCountdown.querySelector("[data-promo-seconds]"),
    };
    const pad = (value) => String(value).padStart(2, "0");
    const getDeadline = () => {
      let storedDeadline = 0;
      try {
        storedDeadline = Number(window.localStorage.getItem(storageKey));
      } catch (error) {
        storedDeadline = 0;
      }
      if (storedDeadline && storedDeadline > Date.now()) {
        return storedDeadline;
      }
      const deadline = Date.now() + duration;
      try {
        window.localStorage.setItem(storageKey, String(deadline));
      } catch (error) {
        // The countdown still works for this page view when storage is unavailable.
      }
      return deadline;
    };
    const deadline = getDeadline();
    const renderCountdown = () => {
      const remaining = Math.max(deadline - Date.now(), 0);
      const totalSeconds = Math.floor(remaining / 1000);
      const days = Math.floor(totalSeconds / 86400);
      const hours = Math.floor((totalSeconds % 86400) / 3600);
      const minutes = Math.floor((totalSeconds % 3600) / 60);
      const seconds = totalSeconds % 60;

      nodes.days.textContent = pad(days);
      nodes.hours.textContent = pad(hours);
      nodes.minutes.textContent = pad(minutes);
      nodes.seconds.textContent = pad(seconds);

      if (remaining <= 0) {
        try {
          window.localStorage.removeItem(storageKey);
        } catch (error) {
          // No storage cleanup is needed when storage is unavailable.
        }
        window.clearInterval(intervalId);
      }
    };
    const intervalId = window.setInterval(renderCountdown, 1000);
    renderCountdown();
  }

  const checkoutForm = document.querySelector("[data-checkout-form]");
  if (checkoutForm) {
    const password = checkoutForm.querySelector("[data-checkout-password='primary']");
    const confirmation = checkoutForm.querySelector("[data-checkout-password='confirm']");
    const passwordFeedback = checkoutForm.querySelector("[data-password-feedback]");

    if (password && confirmation && passwordFeedback) {
      const feedbackId = passwordFeedback.id || "checkout-password-feedback";
      passwordFeedback.id = feedbackId;
      password.setAttribute("aria-describedby", feedbackId);
      confirmation.setAttribute("aria-describedby", feedbackId);

      let passwordTouched = false;
      let confirmationTouched = false;

      const setFeedback = (message, tone = "error") => {
        if (!message) {
          passwordFeedback.hidden = true;
          passwordFeedback.textContent = "";
          passwordFeedback.dataset.tone = "";
          return;
        }
        passwordFeedback.hidden = false;
        passwordFeedback.textContent = message;
        passwordFeedback.dataset.tone = tone;
      };

      const validatePasswords = ({ force = false } = {}) => {
        const passwordValue = password.value.trim();
        const confirmationValue = confirmation.value.trim();
        const shouldShow = force || passwordTouched || confirmationTouched;
        let message = "";
        let target = null;

        password.setCustomValidity("");
        confirmation.setCustomValidity("");
        password.classList.remove("wh-input-invalid");
        confirmation.classList.remove("wh-input-invalid");

        if (shouldShow && passwordValue && passwordValue.length < 8) {
          message = "La contraseña debe tener al menos 8 caracteres.";
          target = password;
          password.setCustomValidity(message);
        } else if (shouldShow && passwordValue && confirmationValue && passwordValue !== confirmationValue) {
          message = "Las contraseñas no coinciden.";
          target = confirmation;
          confirmation.setCustomValidity(message);
        } else if (shouldShow && passwordValue && confirmationValue && passwordValue === confirmationValue) {
          setFeedback("Las contraseñas coinciden.", "success");
          return true;
        }

        if (message) {
          target.classList.add("wh-input-invalid");
          setFeedback(message, "error");
          return false;
        }

        setFeedback("");
        return true;
      };

      password.addEventListener("input", () => {
        passwordTouched = true;
        validatePasswords();
      });
      confirmation.addEventListener("input", () => {
        confirmationTouched = true;
        validatePasswords();
      });
      password.addEventListener("blur", () => {
        passwordTouched = true;
        validatePasswords();
      });
      confirmation.addEventListener("blur", () => {
        confirmationTouched = true;
        validatePasswords();
      });
      checkoutForm.addEventListener("submit", (event) => {
        passwordTouched = true;
        confirmationTouched = true;
        if (!validatePasswords({ force: true }) || !checkoutForm.checkValidity()) {
          event.preventDefault();
          checkoutForm.reportValidity();
        }
      });
    }
  }

  const destinationTrack = document.querySelector("[data-carousel-track]");
  const previousButton = document.querySelector("[data-carousel-prev]");
  const nextButton = document.querySelector("[data-carousel-next]");

  if (destinationTrack && previousButton && nextButton) {
    const scrollToNextCard = (direction) => {
      const firstCard = destinationTrack.querySelector(".wh-destination-card");
      const gap = parseFloat(getComputedStyle(destinationTrack).columnGap || "0");
      const distance = firstCard ? firstCard.getBoundingClientRect().width + gap : 320;
      destinationTrack.scrollBy({ left: distance * direction, behavior: "smooth" });
    };

    const updateButtons = () => {
      const maxScroll = destinationTrack.scrollWidth - destinationTrack.clientWidth - 1;
      previousButton.disabled = destinationTrack.scrollLeft <= 1;
      nextButton.disabled = destinationTrack.scrollLeft >= maxScroll;
    };

    previousButton.addEventListener("click", () => scrollToNextCard(-1));
    nextButton.addEventListener("click", () => scrollToNextCard(1));
    destinationTrack.addEventListener("scroll", updateButtons, { passive: true });
    window.addEventListener("resize", updateButtons);
    destinationTrack.scrollLeft = 0;
    updateButtons();
  }
});
