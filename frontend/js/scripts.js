/*!
* Start Bootstrap - Grayscale v7.0.6 (https://startbootstrap.com/theme/grayscale)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-grayscale/blob/master/LICENSE)
*/
//
// Scripts
// 

window.addEventListener('DOMContentLoaded', event => {

    // Navbar shrink function
    var navbarShrink = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('navbar-shrink')
        } else {
            navbarCollapsible.classList.add('navbar-shrink')
        }

    };

    // Shrink the navbar 
    navbarShrink();

    // Shrink the navbar when page is scrolled
    document.addEventListener('scroll', navbarShrink);

    // Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            rootMargin: '0px 0px -40%',
        });
    };

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });
    // === 联赛背景切换功能 ===
    const leagueButtons = document.querySelectorAll('.league-selector');
    const header = document.querySelector('header.masthead');

    leagueButtons.forEach(button => {
        button.addEventListener('click', function () {
            const league = button.dataset.league;

            // 替换 header 背景类（可组合多个联赛风格）
            header.className = 'masthead masthead-' + league;
        });
    });
    

    document.addEventListener('DOMContentLoaded', () => {
        const roundTab = document.getElementById('roundTab');
        const timetableTab = document.getElementById('timetableTab');
        const roundSelector = document.getElementById('roundSelector');
        const matchList = document.getElementById('matchList');
      
        // Switch between By Round and Timetable
        roundTab.addEventListener('click', () => {
          roundSelector.style.display = 'block';  // Show round selector
          matchList.innerHTML = ''; // Clear match list
          loadRoundMatches(1);  // Load Round 1 by default
        });
      
        timetableTab.addEventListener('click', () => {
          roundSelector.style.display = 'none';  // Hide round selector
          matchList.innerHTML = ''; // Clear match list
          loadTimetableMatches();  // Load timetable matches
        });
      
        // Dynamically generate Round buttons (1 to 38)
        for (let i = 1; i <= 38; i++) {
          const btn = document.createElement('button');
          btn.className = 'btn btn-outline-light round-btn';
          btn.dataset.round = i;
          btn.textContent = `Round ${i}`;
          btn.addEventListener('click', () => loadRoundMatches(i));
          roundSelector.appendChild(btn);
        }
      
        // Load the matches for the selected round
        function loadRoundMatches(round) {
          // Fetch round data from the backend (adjust the URL to your backend structure)
          fetch(`https://albertc9.github.io/TactiTrack/backend/round/61627/${round}.csv`)
            .then(response => response.text())
            .then(data => {
              // Parse CSV data
              const matches = parseCSV(data);
      
              // Clear previous matches
              matchList.innerHTML = '';
      
              // Display the new matches
              matches.forEach(match => {
                const matchItem = document.createElement('a');
                matchItem.className = 'list-group-item list-group-item-action';
                matchItem.textContent = `${match.date} · ${match.homeTeam} vs ${match.awayTeam} · ${match.homeScore} - ${match.awayScore}`;
                matchList.appendChild(matchItem);
              });
            })
            .catch(error => console.error('Error loading match data:', error));
        }
      
        // Load timetable matches (example data)
        function loadTimetableMatches() {
          const data = [
            { home: "Man United", away: "Arsenal", score: "2-1", date: "2024-08-10" },
            { home: "Liverpool", away: "Chelsea", score: "3-2", date: "2024-08-12" }
            // Add real timetable data here
          ];
      
          // Clear previous matches
          matchList.innerHTML = '';
      
          // Display the new matches
          data.forEach(match => {
            const matchItem = document.createElement('a');
            matchItem.className = 'list-group-item list-group-item-action';
            matchItem.textContent = `${match.date} · ${match.home} vs ${match.away} · ${match.score}`;
            matchList.appendChild(matchItem);
          });
        }
      
        // Function to parse CSV text into an array of matches
        function parseCSV(csvText) {
          const rows = csvText.split('\n');
          const matches = [];
          
          // Skip the header row (assumed to be the first row)
          for (let i = 1; i < rows.length; i++) {
            const cells = rows[i].split(',');
      
            // Check if the row has enough columns
            if (cells.length >= 10) {
              const match = {
                matchID: cells[0],
                round: cells[1],
                status: cells[2],
                timestamp: cells[3],
                homeTeam: cells[4],
                awayTeam: cells[5],
                homeScore: cells[6],
                awayScore: cells[7],
                finalResult: cells[8],
                hasXGData: cells[9]
              };
              matches.push(match);
            }
          }
          return matches;
        }
      });
      
      







});