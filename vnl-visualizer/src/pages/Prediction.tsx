
import React, { useState, useEffect, useMemo } from 'react';
import Papa from 'papaparse';
import './Lookup.css';

const COUNTRY_NAMES: Record<string, string> = {
  ARG: 'Argentina', BRA: 'Brazil', BUL: 'Bulgaria', CAN: 'Canada', CHN: 'China', CUB: 'Cuba', FRA: 'France', GER: 'Germany', IRI: 'Iran', ITA: 'Italy', JPN: 'Japan', NED: 'Netherlands', POL: 'Poland', SLO: 'Slovenia', SRB: 'Serbia', TUR: 'Turkey', UKR: 'Ukraine', USA: 'USA',
};

const Prediction: React.FC = () => {
  const [teams, setTeams] = useState<string[]>([]);
  const [team1, setTeam1] = useState('');
  const [team2, setTeam2] = useState('');
  const [team1Search, setTeam1Search] = useState('');
  const [team2Search, setTeam2Search] = useState('');
  useEffect(() => {
    fetch('/merged_stats.csv')
      .then((r) => r.text())
      .then((csvText) => {
        const parsed = Papa.parse(csvText, { header: true, dynamicTyping: false, skipEmptyLines: true });
        const rows = (parsed.data as any[]).filter((r) => r && r['Team']);
        const uniqueTeams = Array.from(new Set(rows.map((r) => r['Team']))).sort();
        setTeams(uniqueTeams);
      });
  }, []);
  const [result, setResult] = useState<null | {
    winner: string;
    winner_confidence: number;
    set_score: string;
    set_score_confidence: number;
  }>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePredict = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const response = await fetch(
        `/api/predict?team1=${encodeURIComponent(team1)}&team2=${encodeURIComponent(team2)}`
      );
      if (!response.ok) throw new Error('Prediction failed');
      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Filtered team dropdowns
  const filteredTeams1 = useMemo(() =>
    teams.filter(t => {
      const name = COUNTRY_NAMES[t] || t;
      return name.toLowerCase().includes(team1Search.toLowerCase()) && t !== team2;
    }),
    [teams, team1Search, team2]
  );
  const filteredTeams2 = useMemo(() =>
    teams.filter(t => {
      const name = COUNTRY_NAMES[t] || t;
      return name.toLowerCase().includes(team2Search.toLowerCase()) && t !== team1;
    }),
    [teams, team2Search, team1]
  );

  return (
    <div className="lookup-container">
      <h1>Match Prediction</h1>
      <p>Select two teams to predict the winner and set score.</p>
  <div className="prediction-search-row" style={{ marginBottom: 32 }}>
  <div style={{ position: 'relative', width: 140 }}>
    <input
      className="lookup-searchbar"
      type="text"
      placeholder="Team 1"
      value={team1Search || (team1 ? (COUNTRY_NAMES[team1] || team1) : '')}
      onChange={e => {
        setTeam1Search(e.target.value);
        setTeam1('');
      }}
      autoComplete="off"
      style={{ width: '100%' }}
    />
    {team1Search && filteredTeams1.length > 0 && !team1 && (
      <ul className="lookup-search-dropdown" style={{ width: '100%' }}>
        {filteredTeams1.map((t, idx) => (
          <li
            key={t + '-' + idx}
            className="lookup-search-dropdown-item"
            onClick={() => {
              setTeam1(t);
              setTeam1Search('');
            }}
          >
            {COUNTRY_NAMES[t] || t}
          </li>
        ))}
      </ul>
    )}
  </div>
  <span className="prediction-vs-text">vs</span>
  <div style={{ position: 'relative', width: 140 }}>
    <input
      className="lookup-searchbar"
      type="text"
      placeholder="Team 2"
      value={team2Search || (team2 ? (COUNTRY_NAMES[team2] || team2) : '')}
      onChange={e => {
        setTeam2Search(e.target.value);
        setTeam2('');
      }}
      autoComplete="off"
      style={{ width: '100%' }}
    />
    {team2Search && filteredTeams2.length > 0 && !team2 && (
      <ul className="lookup-search-dropdown" style={{ width: '100%' }}>
        {filteredTeams2.map((t, idx) => (
          <li
            key={t + '-' + idx}
            className="lookup-search-dropdown-item"
            onClick={() => {
              setTeam2(t);
              setTeam2Search('');
            }}
          >
            {COUNTRY_NAMES[t] || t}
          </li>
        ))}
      </ul>
    )}
  </div>
      </div>
      <button
        className="lookup-group-nav-btn"
        style={{ margin: '0 auto 24px auto', display: 'block', minWidth: 180 }}
        onClick={handlePredict}
        disabled={loading || !team1 || !team2}
      >
        {loading ? 'Predicting...' : 'Predict'}
      </button>
      {error && <div className="lookup-error">{error}</div>}
      {result && (
        <div className="lookup-player-details small" style={{ marginTop: 32 }}>
          <h2>Prediction Result</h2>
          <div className="lookup-player-stats-groups single">
            <div className="lookup-stat-group">
              <div className="lookup-stat-group-label">Winner</div>
              <div className="lookup-stat-group-rows">
                <div className="lookup-stat-row">
                  <span className="lookup-stat-label">Winner</span>
                  <span className="lookup-stat-value">{result.winner}</span>
                </div>
                <div className="lookup-stat-row">
                  <span className="lookup-stat-label">Confidence</span>
                  <span className="lookup-stat-value">{(result.winner_confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
            <div className="lookup-stat-group">
              <div className="lookup-stat-group-label">Set Score</div>
              <div className="lookup-stat-group-rows">
                <div className="lookup-stat-row">
                  <span className="lookup-stat-label">Set Score</span>
                  <span className="lookup-stat-value">{result.set_score}</span>
                </div>
                <div className="lookup-stat-row">
                  <span className="lookup-stat-label">Confidence</span>
                  <span className="lookup-stat-value">{(result.set_score_confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Prediction;
