let newsHeadlines = [];
let currentNewsIndex = 0;
let newsCycleTimer = null;

function loadNews() {
    fetch('/api/news')
        .then(r => r.json())
        .then(data => {
            if (data.success && data.headlines.length > 0) {
                newsHeadlines = data.headlines;
                currentNewsIndex = 0;
                renderNewsDots();
                showNewsItem(0);
                document.getElementById('news-offline-badge').style.display = data.cached ? 'inline' : 'none';

                if (newsCycleTimer) clearInterval(newsCycleTimer);
                if (newsHeadlines.length > 1) {
                    newsCycleTimer = setInterval(cycleNews, 9000);
                }
            } else {
                document.getElementById('news-item').textContent = 'Headlines unavailable';
                document.getElementById('news-dots').innerHTML = '';
            }
        })
        .catch(() => {
            document.getElementById('news-item').textContent = 'Headlines unavailable';
            document.getElementById('news-dots').innerHTML = '';
        });
}

function renderNewsDots() {
    document.getElementById('news-dots').innerHTML = newsHeadlines.map((_, i) =>
        `<span class="news-dot${i === currentNewsIndex ? ' active' : ''}"></span>`
    ).join('');
}

function showNewsItem(index) {
    const el = document.getElementById('news-item');
    const item = newsHeadlines[index];
    el.style.opacity = 0;
    setTimeout(() => {
        el.textContent = item.title;
        el.onclick = item.link ? () => window.open(item.link, '_blank') : null;
        el.classList.toggle('news-item-clickable', !!item.link);
        el.style.opacity = 1;
    }, 300);
}

function cycleNews() {
    currentNewsIndex = (currentNewsIndex + 1) % newsHeadlines.length;
    showNewsItem(currentNewsIndex);
    renderNewsDots();
}