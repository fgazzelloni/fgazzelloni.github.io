document.querySelectorAll('[data-dslc-recordings]').forEach((section) => {
  const cards = Array.from(section.querySelectorAll('.workshop-card'));
  const extraCards = Array.from(section.querySelectorAll('[data-dslc-extra]'));
  const button = section.querySelector('.dslc-toggle');
  const status = section.querySelector('[data-dslc-status]');
  if (!button || extraCards.length === 0) return;

  const initialCount = cards.length - extraCards.length;
  let expanded = false;

  function update() {
    extraCards.forEach((card) => { card.hidden = !expanded; });
    button.setAttribute('aria-expanded', String(expanded));
    button.textContent = expanded
      ? 'Show fewer recordings'
      : `Show all ${cards.length} recordings`;
    status.textContent = `${expanded ? cards.length : initialCount} of ${cards.length} selected recordings`;
  }

  button.addEventListener('click', () => {
    expanded = !expanded;
    update();
    if (expanded) extraCards[0].querySelector('a').focus({ preventScroll: true });
  });

  update();
  button.hidden = false;
});
