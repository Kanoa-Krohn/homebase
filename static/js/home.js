function updateClock() {
    const now = new Date();
    const seconds = now.getSeconds();

    document.getElementById('time').textContent = now.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });

    document.getElementById('date').textContent = now.toLocaleDateString([], {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
});

    const circumference = 119.4;
    const offset = circumference * (1 - seconds / 60);
    const ring = document.getElementById('seconds-ring-progress');
    if (seconds === 0) {
        ring.style.transition = 'none';
        ring.style.strokeDashoffset = circumference;
        void ring.offsetWidth; // force reflow before re-enabling transition
        ring.style.transition = 'stroke-dashoffset 0.9s linear';
    } else {
        ring.style.strokeDashoffset = offset;
    }
    document.getElementById('seconds-ring-text').textContent = seconds;
}

updateClock();
setInterval(updateClock, 1000);


let showingTomorrow = false;
let weatherDayCycleTimer = null;

function renderWeatherDots() {
    document.getElementById('weather-dots').innerHTML = ['Today', 'Tomorrow'].map((_, i) =>
        `<span class="news-dot${(showingTomorrow ? 1 : 0) === i ? ' active' : ''}"></span>`
    ).join('');
}

function lockWeatherCardSize() {
    const dayContent = document.getElementById('weather-day-content');
    dayContent.style.minHeight = '';
    dayContent.style.minWidth = '';

    const rect = dayContent.getBoundingClientRect();
    dayContent.style.minHeight = rect.height + 'px';
    dayContent.style.minWidth = rect.width + 'px';
}

function cycleWeatherDay() {
    const dayContent = document.getElementById('weather-day-content');
    const todayView = document.getElementById('weather-today-view');
    const tomorrowView = document.getElementById('weather-tomorrow-view');

    dayContent.style.opacity = 0;
    setTimeout(() => {
        showingTomorrow = !showingTomorrow;
        todayView.style.display = showingTomorrow ? 'none' : 'block';
        tomorrowView.style.display = showingTomorrow ? 'block' : 'none';
        renderWeatherDots();
        dayContent.style.opacity = 1;
    }, 300);
}

function loadWeather() {
    fetch('/api/weather')
        .then(r => r.json())
        .then(data => {
            const cacheNoteEl = document.getElementById('weather-cache-note');

            if (!data.success) {
                document.getElementById('weather-condition').textContent = 'Unavailable';
                cacheNoteEl.style.display = 'none';
                return;
            }

            cacheNoteEl.style.display = data.from_cache ? 'inline' : 'none';

            document.getElementById('weather-temp').textContent = `${data.temp}°`;
            document.getElementById('weather-temp-c').textContent = `${data.temp_c}°C`;
            document.getElementById('weather-condition').textContent = data.condition;
            document.getElementById('weather-hilo').textContent = `${data.high}° / ${data.low}°`;
            document.getElementById('weather-humidity').textContent = `${data.humidity}%`;
            document.getElementById('weather-rain').textContent = `${data.rain_chance}%`;
            document.getElementById('weather-wind').textContent = data.wind;

            if (data.tomorrow) {
                document.getElementById('weather-tomorrow-high').textContent = `${data.tomorrow.high}°`;
                document.getElementById('weather-tomorrow-condition').textContent = data.tomorrow.condition;
                document.getElementById('weather-tomorrow-hilo').textContent = `${data.tomorrow.high}° / ${data.tomorrow.low}°`;
                document.getElementById('weather-tomorrow-rain').textContent = `${data.tomorrow.rain_chance}%`;
                document.getElementById('weather-tomorrow-humidity').textContent =
                    data.tomorrow.humidity != null ? `${data.tomorrow.humidity}%` : 'N/A';
                document.getElementById('weather-tomorrow-wind').textContent = data.tomorrow.wind || 'N/A';
            }

            showingTomorrow = false;
            document.getElementById('weather-today-view').style.display = 'block';
            document.getElementById('weather-tomorrow-view').style.display = 'none';
            renderWeatherDots();
            lockWeatherCardSize();

            if (weatherDayCycleTimer) clearInterval(weatherDayCycleTimer);
            if (data.tomorrow) {
                weatherDayCycleTimer = setInterval(cycleWeatherDay, 6000);
            }
        })
        .catch(() => {
            document.getElementById('weather-condition').textContent = 'Unavailable';
            document.getElementById('weather-cache-note').style.display = 'none';
        });
}

loadWeather();
setInterval(loadWeather, 10 * 60 * 1000);