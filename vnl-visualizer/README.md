# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

# VNL Predictor

[Live Website](https://vnl-predictor.vercel.app)

## Overview
VNL Predictor is a modern, interactive web application for exploring and visualizing player statistics from the Volleyball Nations League. Built with React and Vite, it features a clean UI, advanced search, and dynamic data visualizations to help users discover insights about top volleyball athletes.

## Features
- **Player Lookup:** Instantly search and view detailed stats for 337+ players, with smooth animations and organized stat categories.
- **Visualization:** Create custom scatter plots to compare players by any stat, filter by team, position, age, and more.
- **Responsive Design:** Optimized for desktop and mobile, with a beautiful, intuitive interface.
- **Fast & Modern Stack:** Built with React, TypeScript, Vite, and Chart.js for performance and maintainability.
- **Automated Data Collection:** All player statistics are gathered using custom Python webscraping scripts, ensuring up-to-date and accurate data from official sources.

## Technologies Used
- React & TypeScript
- Vite
- Chart.js
- PapaParse (CSV parsing)
- Python (webscraping)
- CSS Modules

## Why This Project?
This project demonstrates:
- Advanced front-end engineering and UI/UX design
- Data-driven development and interactive visualizations
- Clean, maintainable code and modern best practices
- Automated data collection and webscraping
- Attention to detail and user experience

## Getting Started
1. Clone the repository:
   ```sh
   git clone https://github.com/owenhoagie/VNL-Predictor.git
   cd VNL-Predictor/vnl-visualizer
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the development server:
   ```sh
   npm run dev
   ```
4. Visit [http://localhost:5173](http://localhost:5173) (or the port shown in your terminal).

## Live Demo
Check out the live site: [https://vnl-predictor.vercel.app](https://vnl-predictor.vercel.app)

## About Me
I'm passionate about building interactive, data-driven web applications that delight users and solve real problems. I also enjoy designing robust webscraping solutions to automate data collection and keep applications fresh and relevant. If you're looking for an intern who can deliver polished, impactful software, let's connect!

---

*Built by Owen Hoag. For questions or collaboration, feel free to reach out!*
