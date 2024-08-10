const protocol = window.location.protocol === 'http:' ? 'ws://' : 'wss://';
const port = window.location.protocol === 'http:' ? '8000' : '443';
const ws = new WebSocket(`${protocol}//${window.location.hostname}:${port}/ws/matchmaking/`);

ws.onopen = function() {
    document.getElementById('status').innerText = 'Connected to matchmaking queue.';
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'match_found' && data.match_url)
    {
        document.getElementById('message').innerHTML += 'Match found ; redirecting to ' + data.match_url + '<br>';
        window.location.href = data.match_url;
    }
    else if (data.message)
        document.getElementById('message').innerHTML += data.message + '<br>';
};

ws.onclose = function() {
    document.getElementById('status').innerText = 'Disconnected from matchmaking queue.';
};
