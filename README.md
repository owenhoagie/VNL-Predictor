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

## Webscraping Approach
A major technical challenge was collecting player statistics from websites where the data is embedded in JavaScript-rendered content. To solve this, I built custom Python scripts using **Selenium** and **ChromeDriver**. This allowed the scraper to fully render pages in a real browser, interact with dynamic elements, and extract the required information reliably—something that traditional requests-based scraping could not achieve. The result is a robust, automated pipeline for keeping the dataset fresh and complete.

## Technologies Used
- React & TypeScript
- Vite
- Chart.js
- PapaParse (CSV parsing)
- Python (Selenium, ChromeDriver webscraping)
- CSS Modules

## Why This Project?
This project demonstrates:
- Advanced front-end engineering and UI/UX design
- Data-driven development and interactive visualizations
- Clean, maintainable code and modern best practices
- Automated data collection and webscraping with Selenium
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
I'm passionate about building interactive, data-driven web applications that delight users and solve real problems. I also enjoy designing robust webscraping solutions—using tools like Selenium and ChromeDriver—to automate data collection and keep applications fresh and relevant. If you're looking for an intern who can deliver polished, impactful software, let's connect!

---

*Built by Owen Hoag. For questions or collaboration, feel free to reach out!*
