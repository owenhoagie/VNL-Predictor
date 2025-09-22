import { useState, useRef, useEffect, useMemo } from 'react';

const STAT_GROUPS = [
  'Attacking',
  'Blocking',
  'Serving',
  'Setting',
  'Defense',
  'Receiving',
  'Other',
];

export type StatGroupFilterProps = {
  selected: string[];
  onChange: (next: string[]) => void;
};

export default function StatGroupFilter({ selected, onChange }: StatGroupFilterProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (!containerRef.current) return;
      if (!containerRef.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return STAT_GROUPS;
    return STAT_GROUPS.filter((g) => g.toLowerCase().includes(q));
  }, [query]);

  const toggle = (group: string) => {
    if (selected.includes(group)) {
      onChange(selected.filter((g) => g !== group));
    } else {
      onChange([...selected, group]);
    }
  };

  const clearAll = () => onChange([]);

  return (
    <div className="ms" ref={containerRef}>
      <label className="label">Stat Groups</label>
      <button type="button" className="ms-control" onClick={() => setOpen((s) => !s)}>
        <div className="ms-values">
          {selected.length === 0 && (
            <span className="ms-placeholder">All Groups</span>
          )}
          {selected.length > 0 && (
            <div className="ms-chips">
              {selected.slice(0, 3).map((g) => (
                <span key={g} className="chip">{g}</span>
              ))}
              {selected.length > 3 && <span className="chip">+{selected.length - 3}</span>}
            </div>
          )}
        </div>
        <span className="ms-caret" aria-hidden>▾</span>
      </button>
      {open && (
        <div className="ms-panel">
          <div className="ms-actions">
            <input
              className="ms-search"
              placeholder="Search..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button type="button" className="reset" onClick={clearAll}>Clear</button>
          </div>
          <div className="ms-list" role="listbox" aria-multiselectable>
            {filtered.map((group) => {
              const checked = selected.includes(group);
              return (
                <label key={group} className={"ms-item" + (checked ? " is-checked" : "")}> 
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggle(group)}
                  />
                  <span>{group}</span>
                </label>
              );
            })}
            {filtered.length === 0 && (
              <div className="ms-empty">No results</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
