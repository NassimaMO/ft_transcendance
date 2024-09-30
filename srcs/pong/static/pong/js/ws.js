let ws = null;
const statusElement = document.getElementById("status");
const game_id = window.game_id

function startWebSocket()
{
    const protocol = window.location.protocol === 'http:' ? 'ws://' : 'wss://';
    const port = window.location.protocol === 'http:' ? '8000' : '443';
    ws = new WebSocket(`${protocol}//${window.location.hostname}:${port}/ws/pong/${game_id}/`);

    
    ws.onopen = function()
    {
        statusElement.textContent = "Connected";
        statusElement.style.color = "#28a745";
    };

    ws.onclose = function(event)
    {
        statusElement.textContent = "Disconnected";
        statusElement.style.color = "red";
        ws = null;
    };

    ws.onerror = function(event)
    {
        statusElement.textContent = "Error occurred. Please try again.";
        statusElement.style.color = "red";
        if (ws)
        {
            ws.close();
        }
    };

    ws.onmessage = function (event)
    {
        const data = JSON.parse(event.data);
        if (data.message)
        {
            messageElement.textContent = data.message;
        }
    };
}

startWebSocket();
