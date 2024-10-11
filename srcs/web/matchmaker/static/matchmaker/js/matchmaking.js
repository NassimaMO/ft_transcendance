let ws = null;
const match_choice_id = window.match_choice_id
const cancelButton = document.getElementById("cancel-button");
const statusElement = document.getElementById("status");

function startWebSocket()
{
    const protocol = window.location.protocol === 'http:' ? 'ws://' : 'wss://';
    const port = window.location.protocol === 'http:' ? '8000' : '443';
    ws = new WebSocket(`${protocol}//${window.location.hostname}:${port}/ws/matchmaking/${match_choice_id}`);

    ws.onopen = function()
    {
        statusElement.textContent = "Connected to matchmaking";
        statusElement.style.color = "#28a745";
    };

    ws.onclose = function(event)
    {
        if (event.code === 1000)
        {
            statusElement.textContent = "Matchmaking cancelled";
            statusElement.style.color = "#ffc107";
        }
        else
        {
            statusElement.textContent = "Disconnected from matchmaking";
            statusElement.style.color = "red";
        }
        document.querySelector(".loader").style.display = "none";
        ws = null;
        cancelButton.textContent = "Join Matchmaking";
        cancelButton.onclick = startMatchmaking;
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
        if (data.type === 'match_found' && data.match_url)
        {
            statusElement.textContent = "Match found !";
            statusElement.style.color = "#28a745";
            window.location.href = data.match_url;
        }
        else if (data.message)
        {
            messageElement.textContent = data.message;
        }
    };
}

function cancelMatchmaking()
{
    if (ws)
    {
        ws.close(1000);
    }
}

function startMatchmaking()
{
    startWebSocket();
    statusElement.textContent = "Connecting...";
    statusElement.style.color = "#ffc107";
    document.querySelector(".loader").style.display = "inline-block";
    cancelButton.textContent = "Cancel Matchmaking";
    cancelButton.onclick = cancelMatchmaking;
}

startWebSocket();
cancelButton.onclick = cancelMatchmaking;