const panels = ['panel-pi', 'panel-home', 'panel-events'];
let currentPanelIndex = panels.indexOf('panel-home');

// Panels register callbacks here to start/stop their own live-data polling
// exactly when they become visible/hidden, without carousel.js needing to
// know anything about what any individual panel actually does.
const panelShowHandlers = {};
const panelHideHandlers = {};

function onPanelShow(panelId, handler) {
    panelShowHandlers[panelId] = handler;
}

function onPanelHide(panelId, handler) {
    panelHideHandlers[panelId] = handler;
}

function showPanel(index) {
    const previousId = panels[currentPanelIndex];
    currentPanelIndex = (index + panels.length) % panels.length;
    const activeId = panels[currentPanelIndex];

    panels.forEach((id, i) => {
        const offset = (i - currentPanelIndex) * 100;
        document.getElementById(id).style.transform = `translateX(${offset}%)`;
    });

    if (previousId !== activeId && panelHideHandlers[previousId]) {
        panelHideHandlers[previousId]();
    }
    if (panelShowHandlers[activeId]) {
        panelShowHandlers[activeId]();
    }
}

function goToPreviousPanel() {
    showPanel(currentPanelIndex - 1);
}

function goToNextPanel() {
    showPanel(currentPanelIndex + 1);
}

function flashNavArrow(el) {
    el.classList.add('pressed');
    setTimeout(() => el.classList.remove('pressed'), 450);
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') {
        e.preventDefault();
        goToPreviousPanel();
    } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        goToNextPanel();
    }
});

showPanel(currentPanelIndex);