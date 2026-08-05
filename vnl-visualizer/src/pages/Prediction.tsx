
import { useEffect, useMemo, useState } from 'react';
import './Lookup.css';
import { COUNTRY_NAMES, loadPlayers } from '../data/playerData';

type PredictionResult = {
  winner: string;
  confidence: number;
  set_score?: {
    score: string;
    probability: number;
  };
};

type ErrorResponse = {
  error?: string;
};

export default function Prediction() {
  const [teams, setTeams] = useState<string[]>([]);
  const [team1, setTeam1] = useState('');
  const [team2, setTeam2] = useState('');
  const [team1Search, setTeam1Search] = useState('');
  const [team2Search, setTeam2Search] = useState('');
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    loadPlayers()
      .then((players) => {
        if (!active) return;
        setTeams(Array.from(new Set(players.map(({ Team }) => Team))).sort());
      })
      .catch((reason: unknown) => {
        if (!active) return;
        setError(reason instanceof Error ? reason.message : 'Failed to load teams');
      });
    return () => {
      active = false;
    };
  }, []);

  const handlePredict = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    // Convert abbreviations to full names if needed
    const team1Full = COUNTRY_NAMES[team1] || team1;
    const team2Full = COUNTRY_NAMES[team2] || team2;
    const requestBody = { team1: team1Full, team2: team2Full };
    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      const contentType = response.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        throw new Error(
          `Prediction service returned an invalid response (${response.status}).`
        );
      }

      const data = await response.json() as PredictionResult & ErrorResponse;
      if (!response.ok || data.error) {
        throw new Error(data.error || 'Prediction failed');
      }
      setResult(data);
    } catch (reason: unknown) {
      const message = reason instanceof Error ? reason.message : 'Unknown error';
      setError(
        message === 'Failed to fetch'
          ? 'Unable to reach the prediction service.'
          : message
      );
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
    <main className="lookup-container prediction-container">
      <header className="lookup-page-header">
        <p className="eyebrow">MATCHUP MODEL</p>
        <h1>Put two teams<br />on the same court.</h1>
        <p>Choose a matchup to estimate the winner, confidence, and likely set score.</p>
      </header>
  <div className="prediction-search-row">
  <div className="prediction-team-field">
    <span className="prediction-team-label">TEAM A</span>
    <input
      className="lookup-searchbar"
      type="text"
      placeholder="Team 1"
      aria-label="Search for team 1"
      value={team1Search || (team1 ? (COUNTRY_NAMES[team1] || team1) : '')}
      onChange={e => {
        setTeam1Search(e.target.value);
        setTeam1('');
      }}
      autoComplete="off"
    />
    {team1Search && filteredTeams1.length > 0 && !team1 && (
      <ul className="lookup-search-dropdown" style={{ width: '100%' }} role="listbox">
        {filteredTeams1.map((t, idx) => (
          <li
            key={t + '-' + idx}
            className="lookup-search-dropdown-item"
            role="option"
            tabIndex={0}
            onClick={() => {
              setTeam1(t);
              setTeam1Search('');
            }}
            onKeyDown={(event) => {
              if (event.key !== 'Enter' && event.key !== ' ') return;
              event.preventDefault();
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
  <div className="prediction-team-field">
    <span className="prediction-team-label">TEAM B</span>
    <input
      className="lookup-searchbar"
      type="text"
      placeholder="Team 2"
      aria-label="Search for team 2"
      value={team2Search || (team2 ? (COUNTRY_NAMES[team2] || team2) : '')}
      onChange={e => {
        setTeam2Search(e.target.value);
        setTeam2('');
      }}
      autoComplete="off"
    />
    {team2Search && filteredTeams2.length > 0 && !team2 && (
      <ul className="lookup-search-dropdown" style={{ width: '100%' }} role="listbox">
        {filteredTeams2.map((t, idx) => (
          <li
            key={t + '-' + idx}
            className="lookup-search-dropdown-item"
            role="option"
            tabIndex={0}
            onClick={() => {
              setTeam2(t);
              setTeam2Search('');
            }}
            onKeyDown={(event) => {
              if (event.key !== 'Enter' && event.key !== ' ') return;
              event.preventDefault();
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
        className="lookup-group-nav-btn prediction-submit"
        onClick={handlePredict}
        disabled={loading || !team1 || !team2}
      >
        {loading ? 'Predicting...' : 'Predict'}
      </button>
      {error && <div className="lookup-error">{error}</div>}
      {result && (
        <div className="lookup-player-details small prediction-result">
          <h2>Prediction Result</h2>
          <div className="lookup-player-stats-groups single">
            <div className="lookup-stat-group">
              <div className="lookup-stat-group-label">Info</div>
              <div className="lookup-stat-group-rows">
                <div className="lookup-stat-row">
                  <span className="lookup-stat-label">Winner</span>
                  <span className="lookup-stat-value">{result.winner}</span>
                </div>
                <div className="lookup-stat-row">
                  <span className="lookup-stat-label">Confidence</span>
                  <span className="lookup-stat-value">{(result.confidence * 100).toFixed(1)}%</span>
                </div>
                {result.set_score && (
                  <>
                    <div className="lookup-stat-row">
                      <span className="lookup-stat-label">Score</span>
                      <span className="lookup-stat-value">{result.set_score.score}</span>
                    </div>
                    <div className="lookup-stat-row">
                      <span className="lookup-stat-label">Set Probability</span>
                      <span className="lookup-stat-value">{(result.set_score.probability * 100).toFixed(1)}%</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
