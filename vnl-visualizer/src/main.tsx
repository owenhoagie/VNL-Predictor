import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import Home from './pages/Home';
import Visualization from './pages/Visualization';
import Lookup from './pages/Lookup';
import NavBar from './components/NavBar';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/visualize" element={<Visualization />} />
  <Route path="/lookup" element={<Lookup />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>
);
