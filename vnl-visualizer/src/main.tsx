import { lazy, StrictMode, Suspense } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import Home from './pages/Home';
import NavBar from './components/NavBar';

const Visualization = lazy(() => import('./pages/Visualization'));
const Lookup = lazy(() => import('./pages/Lookup'));
const Prediction = lazy(() => import('./pages/Prediction'));

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter
      future={{
        v7_relativeSplatPath: true,
        v7_startTransition: true,
      }}
    >
      <NavBar />
      <Suspense fallback={<main className="route-loading">Loading…</main>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/visualize" element={<Visualization />} />
          <Route path="/lookup" element={<Lookup />} />
          <Route path="/predict" element={<Prediction />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  </StrictMode>
);
