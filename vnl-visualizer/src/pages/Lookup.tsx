import { useEffect, useMemo, useState, type Dispatch, type SetStateAction } from "react";
import "./Lookup.css";
import {
  COUNTRY_NAMES,
  formatPosition,
  loadPlayers,
  type PlayerRecord,
} from "../data/playerData";

const statLabels: Record<string, string> = {
  "Player Name": "Player Name",
  "Team": "Team",
  "Position": "Position",
  "Age": "Age",
  "Height": "Height",
  "Impact": "Impact",
  "Attacking Rating": "Attacking Rating",
  "Blocking Rating": "Blocking Rating",
  "Serving Rating": "Serving Rating",
  "Setting Rating": "Setting Rating",
  "Defense Rating": "Defense Rating",
  "Receiving Rating": "Receiving Rating",
  "Running Sets": "Running Sets",
  "Setting Errors": "Setting Errors",
  "Still Sets": "Still Sets",
  "Sets Per Match": "Sets Per Match",
  "Successful Receives": "Successful Receives",
  "Receiving Errors": "Receiving Errors",
  "Service Receptions": "Service Receptions",
  "Receives Per Match": "Receives Per Match",
  "Aces": "Aces",
  "Service Errors": "Service Errors",
  "Service Attempts": "Service Attempts",
  "Serves Per Match": "Serves Per Match",
  "Blocks": "Blocks",
  "Blocking Errors": "Blocking Errors",
  "Rebounds": "Rebounds",
  "Blocks Per Match": "Blocks Per Match",
  "Great Saves": "Great Saves",
  "Defensive Errors": "Defensive Errors",
  "Defensive Receptions": "Defensive Receptions",
  "Digs Per Match": "Digs Per Match",
  "Kills": "Kills",
  "Attacking Errors": "Attacking Errors",
  "Attacking Attempts": "Attacking Attempts",
  "Attacks Per Match": "Attacks Per Match",
};

type StatKey = keyof PlayerRecord;
type StatGroup = { label: string; keys: StatKey[] };

type AnimatedStatsPopupProps = {
  selected: PlayerRecord | null;
  groupIdx: number;
  statGroups: StatGroup[];
  statLabels: Record<string, string>;
  setGroupIdx: Dispatch<SetStateAction<number>>;
};

const STAT_GROUPS: StatGroup[] = [
  {
    label: "Basic Info",
    keys: ["Impact", "Team", "Position", "Age", "Height"],
  },
  {
    label: "Attacking",
    keys: ["Attacking Rating", "Kills", "Attacking Errors", "Attacking Attempts", "Attacks Per Match"],
  },
  {
    label: "Blocking",
    keys: ["Blocking Rating", "Blocks", "Blocking Errors", "Rebounds", "Blocks Per Match"],
  },
  {
    label: "Serving",
    keys: ["Serving Rating", "Aces", "Service Errors", "Service Attempts", "Serves Per Match"],
  },
  {
    label: "Setting",
    keys: ["Setting Rating", "Running Sets", "Setting Errors", "Still Sets", "Sets Per Match"],
  },
  {
    label: "Defense",
    keys: ["Defense Rating", "Great Saves", "Defensive Errors", "Defensive Receptions", "Digs Per Match"],
  },
  {
    label: "Receiving",
    keys: ["Receiving Rating", "Successful Receives", "Receiving Errors", "Service Receptions", "Receives Per Match"],
  },
];

function AnimatedStatsPopup({ selected, groupIdx, statGroups, statLabels, setGroupIdx }: AnimatedStatsPopupProps) {
  const [visible, setVisible] = useState(!!selected);
  useEffect(() => {
    if (selected) {
      setVisible(true);
    } else {
      // Delay hiding to allow fade-out animation
      const timeout = setTimeout(() => setVisible(false), 500); // slightly longer for smoother fade
      return () => clearTimeout(timeout);
    }
  }, [selected]);
  if (!selected && !visible) return null;
  return (
    <div className={`lookup-player-details small${!selected ? ' hide' : ''}`}>
      {selected && (
        <>
          <h2>{selected["Player Name"]}</h2>
          <div className="lookup-player-stats-groups single">
            <div className="lookup-stat-group">
              <div className="lookup-stat-group-label">{statGroups[groupIdx].label}</div>
              <div className="lookup-stat-group-rows">
                {statGroups[groupIdx].keys.map((key) => {
                  let value = selected[key];
                  if (key === "Team") value = COUNTRY_NAMES[String(value)] || value;
                  if (key === "Position") value = formatPosition(String(value));
                  if (key === "Height") value = `${value}cm`;
                  return (
                    <div key={key} className="lookup-stat-row">
                      <span className="lookup-stat-label">{statLabels[key]}</span>
                      <span className="lookup-stat-value">{value}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
          <div className="lookup-group-nav">
            <button
              className="lookup-group-nav-btn"
              disabled={groupIdx === 0}
              onClick={() => setGroupIdx((i) => Math.max(0, i - 1))}
            >
              ← Prev
            </button>
            <span className="lookup-group-nav-label">{statGroups[groupIdx].label}</span>
            <button
              className="lookup-group-nav-btn"
              disabled={groupIdx === statGroups.length - 1}
              onClick={() => setGroupIdx((i) => Math.min(statGroups.length - 1, i + 1))}
            >
              Next →
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default function Lookup() {
  const [players, setPlayers] = useState<PlayerRecord[]>([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<PlayerRecord | null>(null);
  const [groupIdx, setGroupIdx] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    loadPlayers()
      .then((rows) => {
        if (active) setPlayers(rows);
      })
      .catch((reason: unknown) => {
        if (!active) return;
        setError(reason instanceof Error ? reason.message : "Failed to load data");
      });
    return () => {
      active = false;
    };
  }, []);

  const filteredPlayers = useMemo(() => {
    if (!search) return players;
    return players.filter((p) =>
      String(p["Player Name"]).toLowerCase().includes(search.toLowerCase())
    );
  }, [players, search]);

  return (
    <main className="lookup-container">
      <header className="lookup-page-header">
        <p className="eyebrow">ROSTER INDEX</p>
        <h1>Find the player.<br />See the full picture.</h1>
        <p>Search the 2025 men&apos;s VNL field and move through every skill group.</p>
      </header>
      <div className="lookup-searchbar-wrap">
        <input
          className="lookup-searchbar"
          type="text"
          placeholder="Search for a player..."
          aria-label="Search for a player"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setSelected(null);
          }}
          autoComplete="off"
          style={{ width: '100%' }}
        />
        {search && filteredPlayers.length > 0 && !selected && (
          <ul className="lookup-search-dropdown" style={{ width: '100%' }} role="listbox">
            {filteredPlayers.map((p, idx) => (
              <li
                key={p["Player Name"] + '-' + p["Team"] + '-' + p["Position"] + '-' + idx}
                className={`lookup-search-dropdown-item${selected && selected["Player Name"] === p["Player Name"] && selected["Team"] === p["Team"] && selected["Position"] === p["Position"] ? " selected" : ""}`}
                role="option"
                tabIndex={0}
                onClick={() => {
                  setSelected(p);
                  setGroupIdx(0);
                  setSearch(p["Player Name"] as string);
                }}
                onKeyDown={(event) => {
                  if (event.key !== "Enter" && event.key !== " ") return;
                  event.preventDefault();
                  setSelected(p);
                  setGroupIdx(0);
                  setSearch(p["Player Name"]);
                }}
              >
                {p["Player Name"]} - {COUNTRY_NAMES[p["Team"]] || p["Team"]}
              </li>
            ))}
          </ul>
        )}
      </div>
      {error && <div className="lookup-error">{error}</div>}
      {/* Animated player details popup */}
      <AnimatedStatsPopup
        selected={selected}
        groupIdx={groupIdx}
        statGroups={STAT_GROUPS}
        statLabels={statLabels}
        setGroupIdx={setGroupIdx}
      />
    </main>
  );
}
