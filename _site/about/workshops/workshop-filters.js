document.querySelectorAll('[data-workshop-browser]').forEach((browser) => {
  const controls = browser.querySelector('.workshop-controls');
  const search = browser.querySelector('input[type="search"]');
  const topic = browser.querySelector('select');
  const cards = Array.from(browser.querySelectorAll('.workshop-card'));
  const status = browser.querySelector('.workshop-results');
  const empty = browser.querySelector('.workshop-empty');
  const normalise = (text) => text.toLocaleLowerCase().trim();
  const searchText = new Map(cards.map((card) => [card, normalise(card.textContent)]));

  function filterRecordings() {
    const query = normalise(search.value);
    let visible = 0;
    cards.forEach((card) => {
      const matches = (topic.value === 'all' || card.dataset.topic === topic.value)
        && searchText.get(card).includes(query);
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    status.textContent = `${visible} of ${cards.length} recordings · newest first`;
    empty.hidden = visible !== 0;
  }

  search.addEventListener('input', filterRecordings);
  topic.addEventListener('change', filterRecordings);
  controls.hidden = false;
  filterRecordings();
});
