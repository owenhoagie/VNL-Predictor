import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

export default function Home() {
  const navigate = useNavigate();
  return (
    <div className="home-container">
      <h1 className="home-title">Welcome to VNL Visualized</h1>
      <p className="home-desc">
        <strong>VNL Visualized</strong> is an interactive platform for exploring and visualizing player statistics from the Volleyball Nations League. Easily compare players, filter by teams, positions, and stat groups, and create custom scatter plots to uncover insights.
      </p>
      <div className="home-howto">
        <h2>How to Use:</h2>
        <ul>
          <li><strong>Navigate</strong> to the Visualization page using the top navigation bar.</li>
          <li><strong>Filter</strong> players by team, position, age, height, and stat groups.</li>
          <li><strong>Select</strong> X and Y axes to compare different stats.</li>
          <li><strong>Interact</strong> with the scatter plot: click points to view player details.</li>
          <li><strong>Reset</strong> filters anytime to start fresh.</li>
        </ul>
      </div>
      <div className="home-interactive">
        <h2>Try it out!</h2>
        <button className="home-btn" onClick={() => navigate('/visualize')}>Go to Visualization</button>
      </div>
    </div>
  );
}
