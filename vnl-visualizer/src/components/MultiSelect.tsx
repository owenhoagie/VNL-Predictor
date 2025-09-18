import { useEffect, useMemo, useRef, useState } from 'react'

type MultiSelectProps = {
  label: string
  options: string[]
  values: string[]
  onChange: (next: string[]) => void
  placeholder?: string
}

export default function MultiSelect({ label, options, values, onChange, placeholder }: MultiSelectProps) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const containerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (!containerRef.current) return
      if (!containerRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', onDocClick)
    return () => document.removeEventListener('mousedown', onDocClick)
  }, [])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return options
    return options.filter((o) => o.toLowerCase().includes(q))
  }, [options, query])

  const toggle = (opt: string) => {
    if (values.includes(opt)) {
      onChange(values.filter((v) => v !== opt))
    } else {
      onChange([...values, opt])
    }
  }

  const clearAll = () => onChange([])

  return (
    <div className="ms" ref={containerRef}>
      <label className="label">{label}</label>
      <button type="button" className="ms-control" onClick={() => setOpen((s) => !s)}>
        <div className="ms-values">
          {values.length === 0 && (
            <span className="ms-placeholder">{placeholder || 'Select...'}</span>
          )}
          {values.length > 0 && (
            <div className="ms-chips">
              {values.slice(0, 3).map((v) => (
                <span key={v} className="chip">{v}</span>
              ))}
              {values.length > 3 && <span className="chip">+{values.length - 3}</span>}
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
            {filtered.map((opt) => {
              const checked = values.includes(opt)
              return (
                <label key={opt} className={"ms-item" + (checked ? " is-checked" : "")}> 
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggle(opt)}
                  />
                  <span>{opt}</span>
                </label>
              )
            })}
            {filtered.length === 0 && (
              <div className="ms-empty">No results</div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}


