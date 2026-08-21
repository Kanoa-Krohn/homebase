function stopNewsCycle() {
    if (newsCycleTimer) {
        clearInterval(newsCycleTimer);
        newsCycleTimer = null;
    }
}

onPanelShow('panel-events', () => {
    loadEvents();
    loadNews();
});

onPanelHide('panel-events', stopNewsCycle);