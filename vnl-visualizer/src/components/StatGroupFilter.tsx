import { useState, useRef, useEffect } from 'react';

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
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (!containerRef.current) return;
      if (!containerRef.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  const toggle = (group: string) => {
    if (selected.includes(group)) {
      onChange(selected.filter((g) => g !== group));
    } else {
      onChange([...selected, group]);
    }
  };

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
              {selected.map((g) => (
                <span key={g} className="chip">{g}</span>
              ))}
            </div>
          )}
        </div>
        <span className="ms-caret" aria-hidden>▾</span>
      </button>
      {open && (
        <div className="ms-panel">
          <div className="ms-list" role="listbox" aria-multiselectable>
            {STAT_GROUPS.map((group) => {
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
          </div>
        </div>
      )}
    </div>
  );
}
