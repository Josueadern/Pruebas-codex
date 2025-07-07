(function () {
  const PIN = '1234';
  const WEEK_MS = 7 * 24 * 60 * 60 * 1000;
  const pointsEl = document.getElementById('points');
  const tasksEl = document.getElementById('tasks');
  const messageEl = document.getElementById('message');

  function loadData() {
    const data = JSON.parse(localStorage.getItem('weeklyData') || '{}');
    if (!data.startDate) {
      data.startDate = Date.now();
      data.points = 0;
      data.completedTasks = 0;
      localStorage.setItem('weeklyData', JSON.stringify(data));
    }
    return data;
  }

  function saveData(data) {
    localStorage.setItem('weeklyData', JSON.stringify(data));
  }

  function updateView(data) {
    pointsEl.textContent = data.points;
    tasksEl.textContent = data.completedTasks;
  }

  function pushHistory(record) {
    const history = JSON.parse(localStorage.getItem('history') || '[]');
    history.push(record);
    localStorage.setItem('history', JSON.stringify(history));
  }

  function getNextResetTime(from) {
    const d = new Date(from);
    // Set to next Sunday 23:59
    d.setUTCHours(23, 59, 0, 0);
    const day = d.getUTCDay();
    const diff = (7 - day) % 7; // days until Sunday
    d.setUTCDate(d.getUTCDate() + diff);
    if (d.getTime() <= from) {
      d.setUTCDate(d.getUTCDate() + 7);
    }
    return d.getTime();
  }

  function resetWeek(data) {
    const now = Date.now();
    pushHistory({
      weekStart: data.startDate,
      weekEnd: now,
      points: data.points,
      completedTasks: data.completedTasks,
    });
    data.startDate = now;
    data.points = 0;
    data.completedTasks = 0;
    data.lastReset = now;
    saveData(data);
    updateView(data);
  }

  function checkReset(data) {
    const nextReset = getNextResetTime(data.startDate);
    if (Date.now() >= nextReset) {
      resetWeek(data);
    }
  }

  function tick(data) {
    checkReset(data);
  }

  function manualReset(data) {
    const pinValue = document.getElementById('pin').value;
    if (pinValue === PIN) {
      messageEl.textContent = '';
      resetWeek(data);
    } else {
      messageEl.textContent = 'Invalid PIN';
    }
  }

  const data = loadData();
  updateView(data);
  checkReset(data); // check on load in case we missed

  document.getElementById('manual-reset').addEventListener('click', function () {
    manualReset(data);
  });

  setInterval(function () {
    tick(data);
  }, 60 * 1000); // check every minute
})();
