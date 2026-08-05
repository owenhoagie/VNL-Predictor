import { useEffect, useMemo, useState } from 'react'
import {
  Chart,
  Legend,
  LinearScale,
  PointElement,
  Tooltip,
  type ActiveElement,
  type ChartEvent,
  type ChartOptions,
  type TooltipItem,
} from 'chart.js'
import { Scatter } from 'react-chartjs-2'
import MultiSelect from './components/MultiSelect'
import StatAxisSelect from './components/StatAxisSelect'
import StatGroupFilter from './components/StatGroupFilter'
import {
  COUNTRY_CODES,
  COUNTRY_NAMES,
  formatPosition,
  getDisplayLabel,
  loadPlayers,
  type AxisKey,
  type PlayerRecord,
} from './data/playerData'

Chart.register(LinearScale, PointElement, Tooltip, Legend)

function App() {
  const [rawData, setRawData] = useState<PlayerRecord[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [teamsSelected, setTeamsSelected] = useState<string[]>([])
  const [positionsSelected, setPositionsSelected] = useState<string[]>([])
  const [ageRange, setAgeRange] = useState<[number, number]>([0, 100])
  const [heightRange, setHeightRange] = useState<[number, number]>([150, 230])
  const [xKey, setXKey] = useState<AxisKey>('Age')
  const [yKey, setYKey] = useState<AxisKey>('Kills')
  const [statGroupsSelected, setStatGroupsSelected] = useState<string[]>([])

  useEffect(() => {
    let active = true
    loadPlayers()
      .then((players) => {
        if (!active) return
        setRawData(players)
        setLoading(false)
      })
      .catch((reason: unknown) => {
        if (!active) return
        const message = reason instanceof Error ? reason.message : 'Failed to load data'
        setError(message)
        setLoading(false)
      })
    return () => {
      active = false
    }
  }, [])

  // For dropdown: show full country names
  const teams = useMemo(() => Array.from(new Set(rawData.map((r) => COUNTRY_NAMES[r.Team] || r.Team))).sort(), [rawData])
  const positions = useMemo(() => Array.from(new Set(rawData.map((r) => formatPosition(r.Position)))).sort(), [rawData])

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
  }, [ageMinMax])

  useEffect(() => {
    setHeightRange(heightMinMax)
  }, [heightMinMax])

  const filtered = useMemo(() => {
    const selectedTeamCodes = new Set(
      teamsSelected.map((team) => COUNTRY_CODES.get(team) ?? team),
    )
    const selectedPositions = new Set(
      positionsSelected.map((position) => position.toUpperCase()),
    )

    return rawData.filter((r) => {
      if (selectedTeamCodes.size > 0 && !selectedTeamCodes.has(r.Team)) return false
      if (selectedPositions.size > 0 && !selectedPositions.has(r.Position)) return false
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
          backgroundColor: '#d83b20',
          borderColor: '#ffffff',
          borderWidth: 1.5,
          pointRadius: 4.5,
          pointHoverRadius: 7,
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

  const chartOptions = useMemo<ChartOptions<'scatter'>>(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#151719',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        padding: 12,
        cornerRadius: 2,
        callbacks: {
          label: (context: TooltipItem<'scatter'>) => {
            const point = context.raw as (typeof chartPoints)[number]
            const player = point.raw
            return `${player['Player Name']} (${player.Team}) — ${getDisplayLabel(xKey)}: ${point.x}, ${getDisplayLabel(yKey)}: ${point.y}`
          },
        },
      },
    },
    scales: {
      x: {
        title: { display: true, text: getDisplayLabel(xKey), color: '#151719', font: { weight: 700 } },
        ticks: { color: '#697078' },
        grid: { color: '#e6e2da' },
        border: { color: '#c9c4ba' },
        min: axisBounds.xMin,
        max: axisBounds.xMax,
      },
      y: {
        title: { display: true, text: getDisplayLabel(yKey), color: '#151719', font: { weight: 700 } },
        ticks: { color: '#697078' },
        grid: { color: '#e6e2da' },
        border: { color: '#c9c4ba' },
        min: axisBounds.yMin,
        max: axisBounds.yMax,
      },
    },
    animation: { duration: 250 },
    parsing: false,
    onClick: (_event: ChartEvent, elements: ActiveElement[]) => {
      if (elements.length === 0) return
      const first = elements[0]
      setSelected(chartPoints[first.index].raw)
    },
  }), [axisBounds, chartPoints, xKey, yKey])

  const [selected, setSelected] = useState<PlayerRecord | null>(null)

  return (
    <main className="container visualizer-page">
      <header className="header">
        <div>
          <p className="eyebrow">PLAYER EXPLORER</p>
          <h1 className="title">Build your own comparison.</h1>
          <p className="page-intro">
            Filter the field, choose two metrics, and find the players who separate themselves.
          </p>
        </div>
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
        <aside className="panel filter-panel">
          <div className="panel-heading">
            <span>FILTERS</span>
            <span>{filtered.length} / {rawData.length}</span>
          </div>
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
            <StatGroupFilter
              selected={statGroupsSelected}
              onChange={setStatGroupsSelected}
            />
          </div>
          <div className="section">
            <StatAxisSelect
              label="X Axis"
              value={xKey}
              onChange={v => setXKey(v as AxisKey)}
              placeholder="Select X axis stat"
              statGroups={statGroupsSelected}
            />
          </div>
          <div className="section">
            <StatAxisSelect
              label="Y Axis"
              value={yKey}
              onChange={v => setYKey(v as AxisKey)}
              placeholder="Select Y axis stat"
              statGroups={statGroupsSelected}
            />
          </div>
        </aside>
        <section className="panel chart-panel">
          <div className="chartHeader">
            <div>
              <span className="chart-kicker">LIVE RESULT</span>
              <strong>{chartPoints.length} players</strong>
            </div>
            <div className="axis-summary">
              <span>{xKey}</span>
              <i aria-hidden="true">×</i>
              <span>{yKey}</span>
            </div>
          </div>
          {loading && (
            <div className="chartWrap" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--muted)', marginTop: 48 }}>Loading data…</div>
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
                      <span className="chip">Team: {COUNTRY_NAMES[selected.Team] || selected.Team}</span>
                      <span className="chip">Position: {formatPosition(selected.Position)}</span>
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
    </main>
  )
}

export default App
