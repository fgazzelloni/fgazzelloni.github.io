/* Only fetch this site's prebuilt selection; publishers are fetched by the updater. */
(async () => {
  const container = document.getElementById('news-topics');
  const status = document.getElementById('news-status');
  if (!container || !status) return;
  const format = value => new Date(value).toLocaleDateString('en-GB', {day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC'});
  try {
    const response = await fetch('data/news.json', {cache: 'no-store'});
    if (!response.ok) throw new Error('News unavailable');
    const data = await response.json();
    const now = Date.now();
    const cutoff = now - data.freshness_days * 86400000;
    for (const topic of data.topics) {
      const card = document.createElement('section');
      card.className = 'news-topic';
      const heading = document.createElement('h3');
      heading.textContent = topic.title;
      card.append(heading);
      const list = document.createElement('ul');
      const items = data.items.filter(item => item.topic === topic.id && Date.parse(item.published_at) >= cutoff && Date.parse(item.published_at) <= now).slice(0, 2);
      for (const item of items) {
        const url = new URL(item.url);
        if (!['https:', 'http:'].includes(url.protocol)) continue;
        const row = document.createElement('li');
        const link = document.createElement('a');
        link.href = url.href;
        link.textContent = item.title;
        const meta = document.createElement('p');
        meta.className = 'news-meta';
        const time = document.createElement('time');
        time.dateTime = item.published_at;
        time.textContent = format(item.published_at);
        meta.append(`${item.publisher} · `, time);
        row.append(link, meta);
        list.append(row);
      }
      if (list.children.length) card.append(list);
      else {
        const empty = document.createElement('p');
        empty.className = 'news-meta';
        empty.textContent = 'No recent headlines available.';
        card.append(empty);
      }
      container.append(card);
    }
    const failed = Object.values(data.sources).some(source => source.status !== 'ok');
    status.textContent = data.last_updated_at ? `Last successful feed update: ${new Date(data.last_updated_at).toLocaleString('en-GB', {timeZone: 'UTC'})} UTC. ` : 'No successful feed update yet. ';
    status.textContent += `Showing headlines from the past ${data.freshness_days} days. `;
    if (failed) status.textContent += 'Some feeds are unavailable; recent cached headlines may appear. ';
    if (!data.checked_at || now - Date.parse(data.checked_at) > 12 * 3600000) status.textContent += 'Updates are delayed.';
  } catch (error) {
    status.textContent = 'Headlines are temporarily unavailable. Please check back later.';
  }
})();
