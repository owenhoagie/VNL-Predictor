import Papa from 'papaparse'

export const COUNTRY_NAMES: Readonly<Record<string, string>> = {
  ARG: 'Argentina',
  BRA: 'Brazil',
  BUL: 'Bulgaria',
  CAN: 'Canada',
  CHN: 'China',
  CUB: 'Cuba',
  FRA: 'France',
  GER: 'Germany',
  IRI: 'Iran',
  ITA: 'Italy',
  JPN: 'Japan',
  NED: 'Netherlands',
  POL: 'Poland',
  SLO: 'Slovenia',
  SRB: 'Serbia',
  TUR: 'Turkey',
  UKR: 'Ukraine',
  USA: 'USA',
}

export const COUNTRY_CODES = new Map(
  Object.entries(COUNTRY_NAMES).map(([code, name]) => [name, code]),
)

export const numericAxes = [
  'Impact',
  'Attacking Rating',
  'Blocking Rating',
  'Serving Rating',
  'Setting Rating',
  'Defense Rating',
  'Receiving Rating',
  'Age',
  'Height',
  'Kills',
  'Attacking Errors',
  'Attacking Attempts',
  'Attacks Per Match',
  'Blocks',
  'Blocking Errors',
  'Rebounds',
  'Blocks Per Match',
  'Aces',
  'Service Errors',
  'Service Attempts',
  'Serves Per Match',
  'Running Sets',
  'Setting Errors',
  'Still Sets',
  'Sets Per Match',
  'Great Saves',
  'Defensive Errors',
  'Digs Per Match',
  'Defensive Receptions',
  'Successful Receives',
  'Receiving Errors',
  'Service Receptions',
  'Receives Per Match',
] as const

export type AxisKey = (typeof numericAxes)[number]

export type PlayerRecord = {
  'Player Name': string
  Team: string
  Position: string
} & Record<AxisKey, number>

export const STAT_GROUPS = [
  {
    name: 'Ratings',
    stats: [
      'Impact',
      'Attacking Rating',
      'Blocking Rating',
      'Serving Rating',
      'Setting Rating',
      'Defense Rating',
      'Receiving Rating',
    ],
  },
  { name: 'General', stats: ['Age', 'Height'] },
  { name: 'Attacking', stats: ['Kills', 'Attacking Errors', 'Attacking Attempts', 'Attacks Per Match'] },
  { name: 'Blocking', stats: ['Blocks', 'Blocking Errors', 'Rebounds', 'Blocks Per Match'] },
  { name: 'Serving', stats: ['Aces', 'Service Errors', 'Service Attempts', 'Serves Per Match'] },
  { name: 'Setting', stats: ['Running Sets', 'Setting Errors', 'Still Sets', 'Sets Per Match'] },
  { name: 'Defense', stats: ['Great Saves', 'Defensive Errors', 'Digs Per Match', 'Defensive Receptions'] },
  { name: 'Receiving', stats: ['Successful Receives', 'Receiving Errors', 'Service Receptions', 'Receives Per Match'] },
] as const

type CsvPlayerRow = Record<string, string | undefined>

let playersPromise: Promise<PlayerRecord[]> | undefined

function parseHeight(value: string | undefined): number {
  const match = value?.match(/\d+/)
  return match ? Number(match[0]) : Number.NaN
}

function normalizePlayer(row: CsvPlayerRow): PlayerRecord {
  const numericValues = Object.fromEntries(
    numericAxes.map((key) => [
      key,
      key === 'Height' ? parseHeight(row[key]) : Number(row[key]),
    ]),
  ) as Record<AxisKey, number>

  return {
    'Player Name': row['Player Name'] ?? '',
    Team: row.Team ?? '',
    Position: row.Position ?? '',
    ...numericValues,
  }
}

async function fetchPlayers(): Promise<PlayerRecord[]> {
  const response = await fetch('/merged_stats.csv')
  if (!response.ok) {
    throw new Error(`Failed to load player data (${response.status})`)
  }

  const csvText = await response.text()
  const parsed = Papa.parse<CsvPlayerRow>(csvText, {
    header: true,
    dynamicTyping: false,
    skipEmptyLines: true,
  })

  if (parsed.errors.length > 0) {
    throw new Error(`Failed to parse player data: ${parsed.errors[0].message}`)
  }

  return parsed.data
    .filter((row) => Boolean(row['Player Name']))
    .map(normalizePlayer)
}

export function loadPlayers(): Promise<PlayerRecord[]> {
  playersPromise ??= fetchPlayers().catch((error: unknown) => {
    playersPromise = undefined
    throw error
  })
  return playersPromise
}

export function formatPosition(position: string): string {
  return position.replace(/\w+/g, (word) => (
    word.charAt(0) + word.slice(1).toLowerCase()
  ))
}

export function getDisplayLabel(key: string): string {
  if (key === 'Height') return 'Height (cm)'
  if (key === 'Age') return 'Age (years)'
  return key
}
