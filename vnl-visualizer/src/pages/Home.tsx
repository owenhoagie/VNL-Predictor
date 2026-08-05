import { useNavigate } from 'react-router-dom';
import './Home.css';

export default function Home() {
  const navigate = useNavigate();
  return (
    <main className="home-container">
      <section className="home-hero">
        <div className="home-copy">
          <p className="eyebrow">MEN&apos;S VNL · 2025 DATASET</p>
          <h1 className="home-title">
            Read the game.
            <span>Beyond the scoreboard.</span>
          </h1>
          <p className="home-desc">
            Player ratings, team context, and matchup projections—built for
            anyone who wants to see what actually drives winning volleyball.
          </p>
          <div className="home-actions">
            <button className="home-btn home-btn-primary" onClick={() => navigate('/visualize')}>
              Explore the data
              <span aria-hidden="true">↗</span>
            </button>
            <button className="home-btn home-btn-secondary" onClick={() => navigate('/predict')}>
              Run a prediction
            </button>
          </div>
        </div>

        <div className="home-data-card" role="region" aria-label="Dataset summary">
          <div className="data-card-heading">
            <span>DATA SNAPSHOT</span>
            <span>VNL / 25</span>
          </div>
          <dl className="data-card-stats">
            <div>
              <dt>Players indexed</dt>
              <dd>337</dd>
            </div>
            <div>
              <dt>National teams</dt>
              <dd>18</dd>
            </div>
            <div>
              <dt>Player metrics</dt>
              <dd>33</dd>
            </div>
          </dl>
        </div>
      </section>

      <section className="home-guide" aria-labelledby="guide-title">
        <div className="guide-heading">
          <p className="eyebrow">THREE WAYS IN</p>
          <h2 id="guide-title">Start with the question you have.</h2>
        </div>
        <div className="guide-grid">
          <button className="guide-card" onClick={() => navigate('/visualize')}>
            <span className="guide-number">01</span>
            <strong>Compare performance</strong>
            <span>Plot any two metrics and filter the field by team, role, age, or height.</span>
            <i aria-hidden="true">→</i>
          </button>
          <button className="guide-card" onClick={() => navigate('/lookup')}>
            <span className="guide-number">02</span>
            <strong>Scout a player</strong>
            <span>Move from overall impact to the skill-level detail behind the rating.</span>
            <i aria-hidden="true">→</i>
          </button>
          <button className="guide-card" onClick={() => navigate('/predict')}>
            <span className="guide-number">03</span>
            <strong>Test a matchup</strong>
            <span>Put two national teams head-to-head for a winner and projected set score.</span>
            <i aria-hidden="true">→</i>
          </button>
        </div>
      </section>
    </main>
  );
}
