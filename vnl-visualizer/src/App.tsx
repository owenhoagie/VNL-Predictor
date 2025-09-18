import { useEffect, useMemo, useState } from 'react'
import Papa from 'papaparse'
import { Chart, registerables } from 'chart.js'
import { Scatter } from 'react-chartjs-2'
import MultiSelect from './components/MultiSelect'
Chart.register(...registerables)

type PlayerRecord = {
  'Player Name': string
  'Team': string
  'Position': string
  'Age': number
  'Height': number
  'Running Sets': number
  'Setting Errors': number
  'Still Sets': number
  'Sets Per Match': number
  'Successful Receives': number
  'Receiving Errors': number
  'Service Receptions': number
  'Receives Per Match': number
  'Aces': number
  'Service Errors': number
  'Service Attempts': number
  'Serves Per Match': number
  'Blocks': number
  'Blocking Errors': number
  'Rebounds': number
  'Blocks Per Match': number
  'Great Saves': number
  'Defensive Errors': number
  'Defensive Receptions': number
  'Digs Per Match': number
  'Kills': number
  'Attacking Errors': number
  'Attacking Attempts': number
  'Attacks Per Match': number
}

const numericAxes = [
  'Age',
  'Height',
  'Running Sets',
  'Setting Errors',
  'Still Sets',
  'Sets Per Match',
  'Successful Receives',
  'Receiving Errors',
  'Service Receptions',
  'Receives Per Match',
  'Aces',
  'Service Errors',
  'Service Attempts',
  'Serves Per Match',
  'Blocks',
  'Blocking Errors',
  'Rebounds',
  'Blocks Per Match',
  'Great Saves',
  'Defensive Errors',
  'Defensive Receptions',
  'Digs Per Match',
  'Kills',
  'Attacking Errors',
  'Attacking Attempts',
  'Attacks Per Match',
] as const

type AxisKey = typeof numericAxes[number]

function parseHeightToNumber(value: string): number {
  if (!value) return NaN
  const match = value.match(/\d+/)
  return match ? Number(match[0]) : NaN
}

function App() {
  const [rawData, setRawData] = useState<PlayerRecord[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [teamsSelected, setTeamsSelected] = useState<string[]>([])
  const [positionsSelected, setPositionsSelected] = useState<string[]>([])
  const [ageRange, setAgeRange] = useState<[number, number]>([0, 100])
  const [heightRange, setHeightRange] = useState<[number, number]>([150, 230])
  const [xKey, setXKey] = useState<AxisKey>('Kills')
  const [yKey, setYKey] = useState<AxisKey>('Blocks')

  useEffect(() => {
    fetch('/merged_stats.csv')
      .then((r) => {
        if (!r.ok) throw new Error(`Failed to load CSV: ${r.status}`)
        return r.text()
      })
      .then((csvText) => {
        const parsed = Papa.parse(csvText, { header: true, dynamicTyping: false, skipEmptyLines: true })
        const rows = (parsed.data as any[]).filter((r) => r && r['Player Name'])
        const normalized: PlayerRecord[] = rows.map((r) => ({
          'Player Name': r['Player Name'],
          'Team': r['Team'],
          'Position': r['Position'],
          'Age': Number(r['Age']),
          'Height': parseHeightToNumber(String(r['Height'])),
          'Running Sets': Number(r['Running Sets']),
          'Setting Errors': Number(r['Setting Errors']),
          'Still Sets': Number(r['Still Sets']),
          'Sets Per Match': Number(r['Sets Per Match']),
          'Successful Receives': Number(r['Successful Receives']),
          'Receiving Errors': Number(r['Receiving Errors']),
          'Service Receptions': Number(r['Service Receptions']),
          'Receives Per Match': Number(r['Receives Per Match']),
          'Aces': Number(r['Aces']),
          'Service Errors': Number(r['Service Errors']),
          'Service Attempts': Number(r['Service Attempts']),
          'Serves Per Match': Number(r['Serves Per Match']),
          'Blocks': Number(r['Blocks']),
          'Blocking Errors': Number(r['Blocking Errors']),
          'Rebounds': Number(r['Rebounds']),
          'Blocks Per Match': Number(r['Blocks Per Match']),
          'Great Saves': Number(r['Great Saves']),
          'Defensive Errors': Number(r['Defensive Errors']),
          'Defensive Receptions': Number(r['Defensive Receptions']),
          'Digs Per Match': Number(r['Digs Per Match']),
          'Kills': Number(r['Kills']),
          'Attacking Errors': Number(r['Attacking Errors']),
          'Attacking Attempts': Number(r['Attacking Attempts']),
          'Attacks Per Match': Number(r['Attacks Per Match']),
        }))
        setRawData(normalized)
        setLoading(false)
      })
      .catch((e) => {
        console.error(e)
        setError(e.message || 'Failed to load data')
        setLoading(false)
      })
  }, [])

  const teams = useMemo(() => Array.from(new Set(rawData.map((r) => r.Team))).sort(), [rawData])
  const positions = useMemo(() => Array.from(new Set(rawData.map((r) => r.Position))).sort(), [rawData])

  const ageMinMax = useMemo(() => {
    const vals = rawData.map((r) => r.Age).filter((n) => Number.isFinite(n))
    if (vals.length === 0) return [0, 100] as [number, number]
    return [Math.min(...vals), Math.max(...vals)] as [number, number]
  }, [rawData])

  const heightMinMax = useMemo(() => {
    const vals = rawData.map((r) => r.Height).filter((n) => Number.isFinite(n))
    if (vals.length === 0) return [150, 230] as [number, number]
    return [Math.min(...vals), Math.max(...vals)] as [number, number]
  }, [rawData])

  useEffect(() => {
    setAgeRange(ageMinMax)
  }, [ageMinMax[0], ageMinMax[1]])

  useEffect(() => {
    setHeightRange(heightMinMax)
  }, [heightMinMax[0], heightMinMax[1]])

  const filtered = useMemo(() => {
    return rawData.filter((r) => {
      if (teamsSelected.length > 0 && !teamsSelected.includes(r.Team)) return false
      if (positionsSelected.length > 0 && !positionsSelected.includes(r.Position)) return false
      if (Number.isFinite(r.Age)) {
        if (r.Age < ageRange[0] || r.Age > ageRange[1]) return false
      }
      if (Number.isFinite(r.Height)) {
        if (r.Height < heightRange[0] || r.Height > heightRange[1]) return false
      }
      return true
    })
  }, [rawData, teamsSelected, positionsSelected, ageRange, heightRange])

  const chartPoints = useMemo(() => {
    return filtered
      .map((r) => ({ x: r[xKey], y: r[yKey], raw: r }))
      .filter((p) => Number.isFinite(p.x) && Number.isFinite(p.y))
  }, [filtered, xKey, yKey])

  const chartData = useMemo(() => {
    return {
      datasets: [
        {
          label: `${xKey} vs ${yKey}`,
          data: chartPoints,
          backgroundColor: 'rgba(79,70,229,0.85)',
          pointRadius: 4,
          pointHoverRadius: 6,
        },
      ],
    }
  }, [chartPoints, xKey, yKey])

  const axisBounds = useMemo(() => {
    if (chartPoints.length === 0) {
      return { xMin: undefined as number | undefined, xMax: undefined as number | undefined, yMin: undefined as number | undefined, yMax: undefined as number | undefined }
    }
    const xs = chartPoints.map((p) => p.x as number)
    const ys = chartPoints.map((p) => p.y as number)
    const minX = Math.min(...xs)
    const maxX = Math.max(...xs)
    const minY = Math.min(...ys)
    const maxY = Math.max(...ys)
    const padXBase = Math.max(Math.abs(maxX), Math.abs(minX)) || 1
    const padYBase = Math.max(Math.abs(maxY), Math.abs(minY)) || 1
    const padX = padXBase * 0.05
    const padY = padYBase * 0.05
    return {
      xMin: Math.max(0, minX - padX),
      xMax: maxX + padX,
      yMin: Math.max(0, minY - padY),
      yMax: maxY + padY,
    }
  }, [chartPoints])

  const chartOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx: any) => {
            const r: PlayerRecord = ctx.raw.raw
            return `${r['Player Name']} (${r.Team}) — ${xKey}: ${ctx.raw.x}, ${yKey}: ${ctx.raw.y}`
          },
        },
      },
    },
    scales: {
      x: { title: { display: true, text: xKey as string }, min: axisBounds.xMin, max: axisBounds.xMax },
      y: { title: { display: true, text: yKey as string }, min: axisBounds.yMin, max: axisBounds.yMax },
    },
    animation: { duration: 250 },
    parsing: false as const,
    onClick: (_evt: any, elements: any[]) => {
      if (!elements || elements.length === 0) return
      const first = elements[0]
      const r: PlayerRecord = chartPoints[first.index].raw
      setSelected(r)
    },
  }), [chartPoints, xKey, yKey])

  const [selected, setSelected] = useState<PlayerRecord | null>(null)

  return (
    <div className="container">
      <header className="header">
        <h1 className="title">VNL Stats Visualizer</h1>
        <button
          className="reset"
          onClick={() => {
            setTeamsSelected([])
            setPositionsSelected([])
            setAgeRange(ageMinMax)
            setHeightRange(heightMinMax)
            setSelected(null)
          }}
        >
          Reset Filters
        </button>
      </header>
      <div className="layout">
        <aside className="panel">
          <div className="section">
            <MultiSelect
              label="Team"
              options={teams}
              values={teamsSelected}
              onChange={setTeamsSelected}
              placeholder="Select teams"
            />
          </div>
          <div className="section">
            <MultiSelect
              label="Position"
              options={positions}
              values={positionsSelected}
              onChange={setPositionsSelected}
              placeholder="Select positions"
            />
          </div>
          <div className="section">
            <label className="label">Age: {ageRange[0]} - {ageRange[1]}</label>
            <div className="control-row">
              <input
                type="range"
                min={ageMinMax[0]}
                max={ageMinMax[1]}
                value={ageRange[0]}
                onChange={(e) => setAgeRange([Number(e.target.value), Math.max(ageRange[1], Number(e.target.value))])}
                className="range"
              />
              <input
                type="range"
                min={ageMinMax[0]}
                max={ageMinMax[1]}
                value={ageRange[1]}
                onChange={(e) => setAgeRange([Math.min(ageRange[0], Number(e.target.value)), Number(e.target.value)])}
                className="range"
              />
            </div>
            <div className="control-row" style={{ fontSize: 12, color: 'var(--muted)' }}>
              <input type="number" className="number" style={{ width: 80 }} value={ageRange[0]} min={ageMinMax[0]} max={ageMinMax[1]} onChange={(e) => setAgeRange([Number(e.target.value), ageRange[1]])} />
              <span>to</span>
              <input type="number" className="number" style={{ width: 80 }} value={ageRange[1]} min={ageMinMax[0]} max={ageMinMax[1]} onChange={(e) => setAgeRange([ageRange[0], Number(e.target.value)])} />
            </div>
          </div>
          <div className="section">
            <label className="label">Height (cm): {heightRange[0]} - {heightRange[1]}</label>
            <div className="control-row">
              <input
                type="range"
                min={heightMinMax[0]}
                max={heightMinMax[1]}
                value={heightRange[0]}
                onChange={(e) => setHeightRange([Number(e.target.value), Math.max(heightRange[1], Number(e.target.value))])}
                className="range"
              />
              <input
                type="range"
                min={heightMinMax[0]}
                max={heightMinMax[1]}
                value={heightRange[1]}
                onChange={(e) => setHeightRange([Math.min(heightRange[0], Number(e.target.value)), Number(e.target.value)])}
                className="range"
              />
            </div>
            <div className="control-row" style={{ fontSize: 12, color: 'var(--muted)' }}>
              <input type="number" className="number" style={{ width: 80 }} value={heightRange[0]} min={heightMinMax[0]} max={heightMinMax[1]} onChange={(e) => setHeightRange([Number(e.target.value), heightRange[1]])} />
              <span>to</span>
              <input type="number" className="number" style={{ width: 80 }} value={heightRange[1]} min={heightMinMax[0]} max={heightMinMax[1]} onChange={(e) => setHeightRange([heightRange[0], Number(e.target.value)])} />
            </div>
          </div>
          <div className="section">
            <label className="label">X Axis</label>
            <select className="select" value={xKey} onChange={(e) => setXKey(e.target.value as AxisKey)}>
              {numericAxes.map((k) => (
                <option key={k} value={k}>{k}</option>
              ))}
            </select>
          </div>
          <div className="section">
            <label className="label">Y Axis</label>
            <select className="select" value={yKey} onChange={(e) => setYKey(e.target.value as AxisKey)}>
              {numericAxes.map((k) => (
                <option key={k} value={k}>{k}</option>
              ))}
            </select>
          </div>
        </aside>
        <section className="panel">
          <div className="chartHeader">
            <div className="chip">{chartPoints.length} players</div>
            <div className="chip">X: {xKey} · Y: {yKey}</div>
          </div>
          {loading && (
            <div className="chartWrap" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--muted)' }}>Loading data…</div>
          )}
          {!loading && error && (
            <div className="chartWrap" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ff6b6b' }}>{error}</div>
          )}
          {!loading && !error && chartPoints.length === 0 && (
            <div className="chartWrap" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 8, color: 'var(--muted)' }}>
              <div style={{ fontSize: 14 }}>No points to display with current filters.</div>
              <button className="reset" onClick={() => { setTeamsSelected([]); setPositionsSelected([]); setAgeRange(ageMinMax); setHeightRange(heightMinMax); }}>Reset Filters</button>
            </div>
          )}
          {!loading && !error && chartPoints.length > 0 && (
            <div>
              <div className="chartWrap">
                <Scatter data={chartData} options={chartOptions} />
              </div>
              {selected && (
                <div className="details">
                  <div className="card">
                    <div className="cardTitle">{selected['Player Name']}</div>
                    <div className="row">
                      <span className="chip">Team: {selected.Team}</span>
                      <span className="chip">Position: {selected.Position}</span>
                      <span className="chip">Age: {selected.Age}</span>
                      <span className="chip">Height: {selected.Height} cm</span>
                      <span className="chip">{xKey}: {selected[xKey]}</span>
                      <span className="chip">{yKey}: {selected[yKey]}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}

export default App