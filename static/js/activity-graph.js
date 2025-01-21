// static/js/activity-graph.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded, initializing activity graph...');
    initializeActivityGraph();
});

function createDayLabels() {
    const days = document.createElement('div');
    days.className = 'day-labels';
    const dayNames = ['Mon', '', 'Wed', '', 'Fri'];

    dayNames.forEach(day => {
        const label = document.createElement('span');
        label.textContent = day;
        days.appendChild(label);
    });

    return days;
}

function createMonthLabels() {
    const monthLabels = document.createElement('div');
    monthLabels.className = 'activity-labels';
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    months.forEach(month => {
        const label = document.createElement('span');
        label.textContent = month;
        monthLabels.appendChild(label);
    });
    return monthLabels;
}

function createLegend() {
    const legend = document.createElement('div');
    legend.className = 'activity-legend';

    const scale = document.createElement('div');
    scale.className = 'legend-scale';

    const less = document.createElement('span');
    less.textContent = 'Less';
    less.className = 'legend-label';

    const more = document.createElement('span');
    more.textContent = 'More';
    more.className = 'legend-label';

    const boxes = document.createElement('div');
    boxes.className = 'legend-boxes';

    // Create intensity boxes
    for (let i = 0; i < 5; i++) {
        const box = document.createElement('div');
        box.className = `activity-day intensity-${i}`;
        boxes.appendChild(box);
    }

    scale.appendChild(less);
    scale.appendChild(boxes);
    scale.appendChild(more);
    legend.appendChild(scale);

    return legend;
}

function getDateForCell(week, day) {
    // Start from January 1, 2025
    const startYear = 2025;
    const start = new Date(startYear, 0, 1);
    const cellDate = new Date(start);
    cellDate.setDate(start.getDate() + (week * 7) + day);
    return cellDate.toISOString().split('T')[0];
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        weekday: 'long',
        month: 'long',
        day: 'numeric',
        year: 'numeric'
    });
}

function createGridStructure() {
    const gridContainer = document.createElement('div');
    gridContainer.className = 'activity-grid';

    // Calculate weeks from start of 2025 until now
    const startDate = new Date(2025, 0, 1);
    const endDate = new Date(2025, 11, 31);  // End of 2025
    const weeks = Math.ceil((endDate - startDate) / (7 * 24 * 60 * 60 * 1000));
    const days = 7;

    for (let w = 0; w < weeks; w++) {
        const week = document.createElement('div');
        week.className = 'activity-week';

        for (let d = 0; d < days; d++) {
            const day = document.createElement('div');
            day.className = 'activity-day intensity-0';
            const date = getDateForCell(w, d);
            day.dataset.date = date;
            day.title = `No contributions on ${formatDate(date)}`;
            week.appendChild(day);
        }
        gridContainer.appendChild(week);
    }

    return gridContainer;
}

function updateActivityGraph(contributionCalendar) {
    console.log('Updating activity graph with calendar:', contributionCalendar);
    const cells = document.querySelectorAll('.activity-day');
    console.log('Found cells:', cells.length);
    const contributionsMap = new Map();

    // Only process days from 2025
    contributionCalendar.weeks.forEach(week => {
        week.contributionDays.forEach(day => {
            if (day.date.startsWith('2025')) {
                contributionsMap.set(day.date, day.contributionCount);
                console.log(`Found contribution for ${day.date}: ${day.contributionCount}`);
            }
        });
    });

    cells.forEach(cell => {
        const date = cell.dataset.date;
        const count = contributionsMap.get(date) || 0;
        const intensity = getIntensityLevel(count);

        cell.className = `activity-day intensity-${intensity}`;
        cell.title = `${count} contribution${count !== 1 ? 's' : ''} on ${formatDate(date)}`;
    });
}

function getIntensityLevel(count) {
    if (count === 0) return 0;
    if (count <= 3) return 1;
    if (count <= 6) return 2;
    if (count <= 9) return 3;
    return 4;
}

function updateStats(stats) {
    try {
        const statsElements = {
            days: document.getElementById('stat-days'),
            projects: document.getElementById('stat-projects'),
            posts: document.getElementById('stat-posts')
        };

        Object.entries(statsElements).forEach(([key, element]) => {
            if (element && stats[key] !== undefined) {
                element.textContent = stats[key];
            }
        });
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

function fetchActivityData() {
    console.log('Fetching activity data...');
    fetch('/api/activity-data')
        .then(response => {
            console.log('Response received:', response.status);
            return response.json();
        })
        .then(responseData => {
            console.log('Data received:', responseData);
            if (responseData.data && responseData.data.weeks) {
                console.log('Updating graph with contribution data');
                updateActivityGraph(responseData.data);
            } else {
                console.warn('No contribution data found in response');
                console.log('Full response:', responseData);
            }
            if (responseData.stats) {
                console.log('Updating stats:', responseData.stats);
                updateStats(responseData.stats);
            } else {
                console.warn('No stats found in response');
            }
        })
        .catch(error => {
            console.error('Error fetching activity data:', error);
            console.error('Error details:', {
                message: error.message,
                stack: error.stack
            });
        });
}

function initializeActivityGraph() {
    console.log('Looking for container...');
    const container = document.getElementById('activity-graph-container');

    if (!container) {
        console.error('Container not found! Make sure your HTML has <div id="activity-graph-container"></div>');
        return;
    }

    // Clear any existing content
    container.innerHTML = '';

    console.log('Creating wrapper...');
    const wrapper = document.createElement('div');
    wrapper.className = 'activity-wrapper';

    // Add month labels first
    console.log('Creating month labels...');
    wrapper.appendChild(createMonthLabels());

    // Create the main graph section
    console.log('Creating graph section...');
    const graphSection = document.createElement('div');
    graphSection.className = 'graph-section';

    // Add day labels
    console.log('Creating day labels...');
    graphSection.appendChild(createDayLabels());

    // Create and add the grid
    console.log('Creating grid structure...');
    const grid = createGridStructure();
    graphSection.appendChild(grid);

    // Add the graph section to the wrapper
    wrapper.appendChild(graphSection);

    // Create and add the legend
    console.log('Creating legend...');
    const legend = createLegend();
    wrapper.appendChild(legend);

    // Add everything to the container
    console.log('Appending all elements to container...');
    container.appendChild(wrapper);

    console.log('Structure created, fetching data...');
    fetchActivityData();
}