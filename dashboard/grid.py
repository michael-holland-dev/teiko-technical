from typing import Sequence

import pandas as pd
from st_aggrid import AgGrid, DataReturnMode, GridOptionsBuilder, JsCode

from dashboard.style import RED

TEXT_FILTER = {
    "filter": "agTextColumnFilter",
    "filterParams": {"filterOptions": ["contains", "equals", "startsWith"], "buttons": ["reset"]},
}
NUMBER_FILTER = {
    "filter": "agNumberColumnFilter",
    "filterParams": {
        "filterOptions": [
            "greaterThan",
            "greaterThanOrEqual",
            "lessThan",
            "lessThanOrEqual",
            "equals",
            "notEqual",
            "inRange",
        ],
        "defaultOption": "greaterThan",
        "defaultJoinOperator": "AND",
        "maxNumConditions": 4,
        "numAlwaysVisibleConditions": 2,
        "buttons": ["reset"],
    },
}
GRID_CSS = {
    ".ag-root-wrapper": {
        "border": "1px solid rgba(0, 0, 0, 0.1) !important",
        "border-radius": "12px !important",
        "font-family": "Inter, -apple-system, sans-serif !important",
    },
    ".ag-header": {"background-color": "#f9f9f8 !important"},
    ".ag-header-cell-text": {"font-weight": "600 !important", "color": "#111110 !important"},
    ".ag-header-cell-filtered .ag-header-cell-text": {"color": f"{RED} !important"},
    ".ag-filter-icon, .ag-header-cell-filtered .ag-icon": {"color": f"{RED} !important"},
    ".kh": {"display": "flex", "align-items": "center", "gap": "6px", "width": "100%", "min-width": "0"},
    ".kh-label": {
        "font-weight": "600", "color": "#111110", "overflow": "hidden",
        "text-overflow": "ellipsis", "white-space": "nowrap",
    },
    ".kh-filtered .kh-label": {"color": RED},
    ".kh-sort": {"color": RED, "font-weight": "700"},
    ".kh-btn": {
        "margin-left": "auto", "border": "none", "background": "transparent", "cursor": "pointer",
        "font-size": "18px", "line-height": "1", "padding": "4px 6px", "border-radius": "6px",
        "color": "#6e6e6a",
    },
    ".kh-btn:hover": {"background": "rgba(0, 0, 0, 0.06)", "color": "#111110"},
    ".kh-menu": {
        "position": "fixed", "z-index": "10000", "width": "180px", "padding": "6px",
        "background": "#ffffff", "border": "1px solid rgba(0, 0, 0, 0.18)", "border-radius": "10px",
        "box-shadow": "0 8px 24px rgba(0, 0, 0, 0.12)",
        "font-family": "Inter, -apple-system, sans-serif", "font-size": "14px",
    },
    ".kh-item": {
        "display": "block", "width": "100%", "text-align": "left", "border": "none",
        "background": "transparent", "padding": "8px 10px", "border-radius": "6px",
        "cursor": "pointer", "color": "#111110", "font": "inherit",
    },
    ".kh-item:hover:not(:disabled)": {"background": "rgba(255, 53, 52, 0.08)", "color": RED},
    ".kh-item:disabled": {"color": "#9f9f9b", "cursor": "default"},
    ".kh-active": {"color": RED, "font-weight": "600"},
    ".kh-divider": {"height": "1px", "margin": "4px 2px", "background": "rgba(0, 0, 0, 0.1)"},
}
PERCENT_FORMATTER = JsCode("function(p) { return p.value == null ? '' : p.value.toFixed(2); }")

KEBAB_HEADER = JsCode(
    """
class KebabHeader {
  init(params) {
    this.params = params;
    const gui = document.createElement('div');
    gui.className = 'kh';
    gui.innerHTML =
      '<span class="kh-label"></span><span class="kh-sort"></span>' +
      '<button type="button" class="kh-btn" aria-label="Column options">&#8942;</button>';
    gui.querySelector('.kh-label').textContent = params.displayName;
    this.eGui = gui;
    this.sortEl = gui.querySelector('.kh-sort');
    this.btn = gui.querySelector('.kh-btn');
    this.onBtn = (e) => { e.stopPropagation(); this.toggleMenu(); };
    this.btn.addEventListener('click', this.onBtn);
    this.onSort = () => this.render();
    this.onFilter = () => this.render();
    params.column.addEventListener('sortChanged', this.onSort);
    params.column.addEventListener('filterChanged', this.onFilter);
    this.render();
  }
  getGui() { return this.eGui; }
  refresh() { return false; }
  render() {
    const sort = this.params.column.getSort();
    this.sortEl.textContent = sort === 'asc' ? '\u2191' : sort === 'desc' ? '\u2193' : '';
    this.eGui.classList.toggle('kh-filtered', this.params.column.isFilterActive());
  }
  toggleMenu() {
    if (this.menu) { this.closeMenu(); return; }
    document.querySelectorAll('.kh-menu').forEach((m) => m.remove());
    const colId = this.params.column.getColId();
    const api = this.params.api;
    const sort = this.params.column.getSort();
    const items = [
      ['Sort ascending', () => this.params.setSort('asc'), sort === 'asc'],
      ['Sort descending', () => this.params.setSort('desc'), sort === 'desc'],
      ['Clear sort', () => this.params.setSort(null), false, !sort],
      'divider',
      ['Filter\u2026', () => api.showColumnFilter(colId), this.params.column.isFilterActive()],
    ];
    if (this.params.column.isFilterActive()) {
      items.push(['Clear filter', () => { api.setColumnFilterModel(colId, null).then(() => api.onFilterChanged()); }]);
    }
    const menu = document.createElement('div');
    menu.className = 'kh-menu';
    items.forEach((item) => {
      if (item === 'divider') { const hr = document.createElement('div'); hr.className = 'kh-divider'; menu.appendChild(hr); return; }
      const [label, action, active, disabled] = item;
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'kh-item' + (active ? ' kh-active' : '');
      b.textContent = label;
      b.disabled = !!disabled;
      b.addEventListener('click', (e) => { e.stopPropagation(); this.closeMenu(); setTimeout(action, 0); });
      menu.appendChild(b);
    });
    const r = this.btn.getBoundingClientRect();
    menu.style.top = (r.bottom + 4) + 'px';
    menu.style.left = Math.max(4, Math.min(r.right - 180, window.innerWidth - 184)) + 'px';
    document.body.appendChild(menu);
    this.menu = menu;
    this.onDoc = (e) => { if (!menu.contains(e.target)) this.closeMenu(); };
    setTimeout(() => document.addEventListener('click', this.onDoc), 0);
  }
  closeMenu() {
    if (!this.menu) return;
    this.menu.remove();
    this.menu = null;
    document.removeEventListener('click', this.onDoc);
  }
  destroy() {
    this.closeMenu();
    this.btn.removeEventListener('click', this.onBtn);
    this.params.column.removeEventListener('sortChanged', this.onSort);
    this.params.column.removeEventListener('filterChanged', this.onFilter);
  }
}
"""
)


def filter_table(
    df: pd.DataFrame,
    key: str,
    text_columns: Sequence[str] = (),
    number_columns: Sequence[str] = (),
    percent_columns: Sequence[str] = (),
    height: int = 460,
) -> pd.DataFrame:
    """Render a DataFrame as an AG Grid with a sort and filter menu in each header. Text columns
    get contains/equals/starts-with filters; number and percent columns get comparison filters
    (percent columns also show two decimals). Returns the rows left after the user's filters.
    """
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        sortable=True,
        resizable=True,
        floatingFilter=False,
        headerComponent=KEBAB_HEADER,
        suppressHeaderMenuButton=True,
        suppressHeaderFilterButton=True,
    )
    for col in text_columns:
        gb.configure_column(col, **TEXT_FILTER)
    for col in number_columns:
        gb.configure_column(col, type=["numericColumn"], **NUMBER_FILTER)
    for col in percent_columns:
        gb.configure_column(
            col, type=["numericColumn"], valueFormatter=PERCENT_FORMATTER, **NUMBER_FILTER
        )
    gb.configure_grid_options(
        autoSizeStrategy={"type": "fitGridWidth"},
        animateRows=False,
    )
    response = AgGrid(
        df,
        gridOptions=gb.build(),
        height=height,
        update_on=["filterChanged"],
        data_return_mode=DataReturnMode.FILTERED,
        allow_unsafe_jscode=True,
        theme="light",
        custom_css=GRID_CSS,
        show_toolbar=False,
        show_search=False,
        show_download_button=False,
        key=key,
    )
    filtered = response["data"]
    return df if filtered is None else pd.DataFrame(filtered)


def summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """Render the cell frequency summary table. Returns the rows left after the user's filters."""
    return filter_table(
        df,
        key="summary_table",
        text_columns=("sample", "population"),
        number_columns=("total_count", "count"),
        percent_columns=("percentage",),
    )
