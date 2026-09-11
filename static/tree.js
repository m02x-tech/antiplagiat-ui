// Сворачивание дерева на странице «Структура программы».
// Та же логика, что во встроенном скрипте antiplagiat.html: видимость строк
// выводится из data-атрибутов depth/has-children/collapsed.
(function() {
  const table = document.getElementById("tree-table");
  if (!table) return;
  const rows = Array.from(table.tBodies[0].rows);

  function updateVisibility() {
    let hideUntilDepth = null;
    for (const row of rows) {
      const depth = parseInt(row.dataset.depth || "0", 10);
      if (hideUntilDepth !== null && depth > hideUntilDepth) {
        row.style.display = "none";
        continue;
      }
      hideUntilDepth = null;
      row.style.display = "";
      if (row.dataset.hasChildren === "1" && row.dataset.collapsed === "1") {
        hideUntilDepth = depth;
      }
    }
    for (const row of rows) {
      const toggle = row.querySelector(".toggle");
      if (toggle && row.dataset.hasChildren === "1") {
        toggle.textContent = row.dataset.collapsed === "1" ? "▸" : "▾";
      }
    }
  }

  table.tBodies[0].addEventListener("click", function(event) {
    const toggle = event.target.closest(".toggle");
    if (!toggle) return;
    const row = toggle.closest("tr");
    row.dataset.collapsed = row.dataset.collapsed === "1" ? "0" : "1";
    updateVisibility();
  });

  const expandAll = document.getElementById("expand-all");
  const collapseAll = document.getElementById("collapse-all");
  if (expandAll) {
    expandAll.addEventListener("click", function() {
      for (const row of rows) row.dataset.collapsed = "0";
      updateVisibility();
    });
  }
  if (collapseAll) {
    collapseAll.addEventListener("click", function() {
      for (const row of rows) row.dataset.collapsed = "1";
      updateVisibility();
    });
  }

  updateVisibility();
})();
