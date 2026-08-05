import { useState, useRef, useEffect, useMemo } from 'react';
import { STAT_GROUPS } from '../data/playerData';

export type StatAxisSelectProps = {
  label: string;
  value: string;
  onChange: (next: string) => void;
  placeholder?: string;
  statGroups?: string[];
};

export default function StatAxisSelect({ label, value, onChange, placeholder, statGroups }: StatAxisSelectProps) {
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

  // If no statGroups, show all stats
  const visibleStats = useMemo(() => {
    let stats: string[] = [];
    if (!statGroups || statGroups.length === 0) {
      stats = STAT_GROUPS.flatMap(g => g.stats);
    } else {
      stats = STAT_GROUPS.filter(g => statGroups.includes(g.name)).flatMap(g => g.stats);
    }
    const q = query.trim().toLowerCase();
    if (!q) return stats;
    return stats.filter(s => s.toLowerCase().includes(q));
  }, [statGroups, query]);

  return (
    <div className="ms" ref={containerRef}>
      <label className="label">{label}</label>
      <button
        type="button"
        className="ms-control"
        onClick={() => setOpen((current) => !current)}
        aria-expanded={open}
        aria-haspopup="listbox"
      >
        <div className="ms-values">
          {!value && (
            <span className="ms-placeholder">{placeholder || 'Select...'}</span>
          )}
          {value && (
            <span className="chip">{value}</span>
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
              aria-label={`Search ${label.toLowerCase()} options`}
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
          <div className="ms-list" role="listbox" aria-multiselectable={false}>
            {visibleStats.map(opt => (
              <label key={opt} className={"ms-item" + (value === opt ? " is-checked" : "")}> 
                <input
                  type="radio"
                  checked={value === opt}
                  onChange={() => { onChange(opt); setOpen(false); }}
                />
                <span>{opt}</span>
              </label>
            ))}
            {visibleStats.length === 0 && (
              <div className="ms-empty">No results</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
