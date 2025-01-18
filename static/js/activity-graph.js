// static/js/activity-graph.js

document.addEventListener('DOMContentLoaded', function() {
    initializeActivityGraph();
});

function initializeActivityGraph() {
    const container = document.getElementById('activity-graph');
    if (!container) return;

    // Create grid structure
    createGridStructure(container);

    // Fetch and populate data
    fetchActivityData();
}

function createGridStructure(container) {
    const weeks = 52;
    const days = 7;

    for (let w = 0; w < weeks; w++) {
        const week = document.createElement('div');
        week.className = 'activity-week';

        for (let d = 0; d < days; d++) {
            const day = document.createElement('div');
            day.className = 'activity-day';
            const date = getDateForCell(w, d);
            day.dataset.date = date;
            day.title = `No activity on ${date}`;
            week.appendChild(day);
        }
        container.appendChild(week);
    }
}

function getDateForCell(week, day) {
    const today = new Date();
    const end = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const start = new Date(end);
    start.setDate(end.getDate() - ((52 * 7) - (week * 7) - day));
    return start.toISOString().split('T')[0];
}

function fetchActivityData() {
    fetch('/api/activity-data')
        .then(response => response.json())
        .then(data => {
            updateActivityGraph(data.activity_data);
            updateStats(data.stats);
        })
        .catch(error => console.error('Error fetching activity data:', error));
}

function updateActivityGraph(activityData) {
    const cells = document.querySelectorAll('.activity-day');
    cells.forEach(cell => {
        const date = cell.dataset.date;
        const count = activityData[date] || 0;
        const intensity = getIntensityLevel(count);

        cell.className = `activity-day intensity-${intensity}`;
        cell.title = `${count} activities on ${date}`;
    });
}

function getIntensityLevel(count) {
    if (!count) return 0;
    if (count <= 2) return 1;
    if (count <= 4) return 2;
    if (count <= 6) return 3;
    return 4;
}

function updateStats(stats) {
    document.getElementById('stat-days').textContent = stats.days;
    document.getElementById('stat-projects').textContent = stats.projects;
    document.getElementById('stat-posts').textContent = stats.posts;
}