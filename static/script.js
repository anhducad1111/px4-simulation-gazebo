async function sendCommand(type, value) {
    await fetch('/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [type]: value })
    });
}

async function sendAction(action) {
    const response = await fetch('/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
    });
    const result = await response.json();
    alert(result.status || 'Action complete');
}
