(() => {
  const filters = document.getElementById('rf-filters');
  if (!filters) return;
  filters.hidden = false;
  const search = document.getElementById('rf-search');
  const status = document.getElementById('rf-status');
  const entries = [...document.querySelectorAll('.rf-entry')];
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  function update() {
    const query = normalize(search.value.trim());
    let visible = 0;
    for (const entry of entries) {
      const summary = entry.querySelector('.rf-entry-summary');
      entry.hidden = !(normalize(summary.textContent).includes(query) &&
        (status.value === 'all' || entry.dataset.state === status.value));
      if (!entry.hidden) visible++;
    }
    document.getElementById('rf-results').textContent = `${visible} de ${entries.length} requisitos`;
    document.getElementById('rf-empty-search').hidden = visible !== 0;
  }
  search.addEventListener('input', update);
  status.addEventListener('change', update);
  update();
})();
