import React, { useEffect, useState, useMemo } from "react";
import Papa from "papaparse";
import "./Lookup.css";


const COUNTRY_NAMES: Record<string, string> = {
  ARG: 'Argentina', BRA: 'Brazil', BUL: 'Bulgaria', CAN: 'Canada', CHN: 'China', CUB: 'Cuba', FRA: 'France', GER: 'Germany', IRI: 'Iran', ITA: 'Italy', JPN: 'Japan', NED: 'Netherlands', POL: 'Poland', SLO: 'Slovenia', SRB: 'Serbia', TUR: 'Turkey', UKR: 'Ukraine', USA: 'USA',
};

function formatPosition(pos: string) {
  return pos.replace(/\w+/g, w => w.charAt(0) + w.slice(1).toLowerCase());
}

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

type PlayerRecord = Record<string, string | number>;

type StatGroup = { label: string; keys: string[] };

type AnimatedStatsPopupProps = {
  selected: PlayerRecord | null;
  groupIdx: number;
  statGroups: StatGroup[];
  statLabels: Record<string, string>;
  setGroupIdx: React.Dispatch<React.SetStateAction<number>>;
};

const AnimatedStatsPopup: React.FC<AnimatedStatsPopupProps> = ({ selected, groupIdx, statGroups, statLabels, setGroupIdx }) => {
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
};

const Lookup: React.FC = () => {
  const [players, setPlayers] = useState<PlayerRecord[]>([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<PlayerRecord | null>(null);
  const [groupIdx, setGroupIdx] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/merged_stats.csv")
      .then((r) => {
        if (!r.ok) throw new Error(`Failed to load CSV: ${r.status}`);
        return r.text();
      })
      .then((csvText) => {
        const parsed = Papa.parse(csvText, { header: true, dynamicTyping: false, skipEmptyLines: true });
        const rows = (parsed.data as any[]).filter((r) => r && r["Player Name"]);
        setPlayers(rows);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message || "Failed to load data");
        setLoading(false);
      });
  }, []);

  const filteredPlayers = useMemo(() => {
    if (!search) return players;
    return players.filter((p) =>
      String(p["Player Name"]).toLowerCase().includes(search.toLowerCase())
    );
  }, [players, search]);

  // Stat groups for organization
  const statGroups = [
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

  return (
    <div className="lookup-container">
      <h1>Player Lookup</h1>
      <p>Type a player's name to view their full stats.</p>
      <div className="lookup-searchbar-wrap">
        <input
          className="lookup-searchbar"
          type="text"
          placeholder="Search for a player..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setSelected(null);
          }}
          autoComplete="off"
        />
        {search && filteredPlayers.length > 0 && !selected && (
          <ul className="lookup-search-dropdown">
            {filteredPlayers.map((p) => (
              <li
                key={p["Player Name"] as string}
                className={`lookup-search-dropdown-item${selected && selected["Player Name"] === p["Player Name"] ? " selected" : ""}`}
                onClick={() => {
                  setSelected(p);
                  setGroupIdx(0);
                  setSearch(p["Player Name"] as string);
                }}
              >
                {p["Player Name"]}
              </li>
            ))}
          </ul>
        )}
      </div>
      {loading && <div className="lookup-loading">Loading players…</div>}
      {error && <div className="lookup-error">{error}</div>}
      {/* Animated player details popup */}
      <AnimatedStatsPopup
        selected={selected}
        groupIdx={groupIdx}
        statGroups={statGroups}
        statLabels={statLabels}
        setGroupIdx={setGroupIdx}
      />
    </div>
  );
};

export default Lookup;
