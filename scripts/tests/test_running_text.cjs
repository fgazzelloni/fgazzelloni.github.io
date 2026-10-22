const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../running-text.js'), 'utf8');

function setup({ reduce = false, legacy = false } = {}) {
  const timers = new Map();
  const events = {};
  const banner = { textContent: '', isConnected: true };
  let nextId = 0;
  let onMotionChange;
  const media = { matches: reduce };
  media[legacy ? 'addListener' : 'addEventListener'] = (...args) => {
    onMotionChange = args.at(-1);
  };
  vm.runInNewContext(source, {
    document: { readyState: 'complete', querySelector: () => banner },
    window: {
      matchMedia: () => media,
      setTimeout(fn, delay) { timers.set(++nextId, { fn, delay }); return nextId; },
      clearTimeout(id) { timers.delete(id); },
      addEventListener(name, fn) { events[name] = fn; }
    }
  });
  return {
    banner, timers, events,
    tick() {
      const [id, { fn, delay }] = timers.entries().next().value;
      timers.delete(id);
      fn();
      return delay;
    },
    changeMotion(value) { media.matches = value; onMotionChange(); }
  };
}

test('reduced motion cycles complete messages slowly, including legacy Safari', () => {
  for (const legacy of [false, true]) {
    const page = setup({ reduce: true, legacy });
    const first = page.banner.textContent;
    const seen = new Set([first]);
    for (let i = 0; i < 4; i++) {
      assert.equal(page.tick(), 8000);
      assert.ok(page.banner.textContent.length > 15);
      seen.add(page.banner.textContent);
      assert.equal(page.timers.size, 1);
    }
    assert.equal(seen.size, 4);
    assert.equal(page.banner.textContent, first);
  }
});

test('desktop typing remains nonempty and advances through every message', () => {
  const page = setup();
  const seen = new Set();
  for (let i = 0; i < 1500; i++) {
    seen.add(page.banner.textContent);
    page.tick();
    assert.ok(page.banner.textContent.length > 0);
    assert.equal(page.timers.size, 1);
  }
  assert.ok(seen.has('Health Metrics and the Spread of Infectious Diseases'));
  assert.ok(seen.has('New book in progress: Mortality 🔍 Analytics - more info coming soon 🔥'));
});

test('navigation and motion changes restart with one timer', () => {
  const page = setup({ legacy: true });
  page.events.pageshow();
  assert.equal(page.timers.size, 1);
  page.changeMotion(true);
  assert.equal(page.timers.size, 1);
  assert.equal(page.tick(), 8000);
  page.events.pagehide();
  assert.equal(page.timers.size, 0);
  page.events.pageshow();
  assert.equal(page.timers.size, 1);
  page.changeMotion(false);
  assert.equal(page.tick(), 2400);
  assert.equal(page.banner.textContent, 'Welcome to my Websit');
});
