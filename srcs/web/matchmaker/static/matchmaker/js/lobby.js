let lobby = null
let lobby_player = null
const protocol = window.location.protocol === 'http:' ? 'ws://' : 'wss://';
const port = window.location.protocol === 'http:' ? '8000' : '443';
let ws = null
const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

async function APIRequest(url, data=null, http_method='GET')
{
    try
    {
        const options = {
            method: http_method,
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
        };
        if (data && (http_method === 'POST' || http_method === 'PUT' || http_method === 'PATCH' || http_method === 'DELETE'))
        {
            options.body = JSON.stringify(data);
        }
        const response = await fetch(url, options); 
        const jsonResponse = await response.json();
        if (!response.ok)
        {
            if (jsonResponse.errors) {
                for (const [key, message] of Object.entries(jsonResponse.errors))
                {
                    console.error(`Erreur (${key}): ${message}`);
                }
            }
            else
            {
                console.error('Une erreur inattendue est survenue.');
            }
        }
        if (jsonResponse.message)
        {
            console.log("Message from API : ", jsonResponse.message);
        }
        return jsonResponse;
    }
    catch (error)
    {
        console.error('Erreur lors de la requête:', error);
    }
}

async function updateLobbyVar()
{
    try
    {
        const data = await APIRequest('/api/users/me/lobbies/main/');
        lobby = data.lobby;
        lobby_player = lobby.members[0];
    }
    catch (error)
    {
        console.error("Failed to fetch lobby data:", error);
    }
}

async function initWebSocket()
{
    ws = new WebSocket(`${protocol}//${window.location.hostname}:${port}/ws/lobby`);
    ws.onmessage = async function(event)
    {
        const data = JSON.parse(event.data);
        if (data.type == "notif")
        {
            await updateLobbyVar();
            for (const change of data.changes)
            {
                switch (change.type)
                {
                    case "join":
                        updateSection('lobby-list');
                        updateSection('lobby-players');
                        if (change.username)
                        {
                            console.log(change.username, "joined the lobby");
                        }
                        else
                        {
                            console.log("A player joined the lobby");
                        }
                        break;
                    case "leave":
                        updateSection('lobby-list');
                        updateSection('lobby-players');
                        if (change.username)
                        {
                            console.log(change.username, "left the lobby");
                        }
                        else
                        {
                            console.log("A player left the lobby");
                        }
                        break;
                    case "lobby":
                        updateSection('lobby-list');
                        updateSection('lobby-players');
                        updateSection('lobby-modes');
                        console.log("You have joined the lobby");
                        break;
                    case "friend-request":
                        updateSection("friend-requests");
                        break;
                    case "friend":
                        updateSection("friends-list");
                        updateSection("invite-banner");
                        break;
                    case "lobby-request":
                        updateSection("lobby-requests");
                        if (change.username)
                        {
                            console.log("New lobby request received from ", change.username);
                        }
                        else
                        {
                            console.log("Lobby request changes");
                        }
                        break;
                    case "match-choice":
                        updateSection("lobby-modes");
                        break;
                    default:
                        console.log("Unhandled change:", change.type);
                }
            }            
        }
    };
}

function updateSection(section)
{
    let url = null;

    if (section === 'lobby-modes')
    {
        url = '/lobby/modes/';
        console.log("Lobby: ", lobby)
    }
    else if (section === 'lobby-players')
    {
        url = '/lobby/players/';
    }
    else if (section === 'friend-requests')
    {
        url = '/lobby/requests/friends/';
    }
    else if (section === 'lobby-requests')
    {
        url = '/lobby/requests/lobby/';
    }
    else if (section === 'friends-list')
    {
        url = '/lobby/list/friends/';
    }
    else if (section === 'lobby-list')
    {
        url = '/lobby/list/';
    }
    else if (section === 'invite-banner')
    {
        url = '/lobby/invite_banner/';
    }
    if (url)
    {
        console.log("updating section : ", section)
        fetch(url)
            .then(response => response.text())
            .then(html => {
                document.getElementById(`${section}`).innerHTML = html;
            })
            .catch(error => console.error('Erreur de mise à jour de la section:', error));
    }
    else
    {
        console.error('Erreur de mise à jour de la section: url indisponible')
    }
}

function toggleSection(sectionId)
{
    const section = document.getElementById(sectionId);
    if (section)
    {
        section.classList.toggle('visible');
    }
}

function openModeSelection()
{
    document.getElementById('modeSelectionModal').style.display = 'flex';
}

function closeModeSelection()
{
    document.getElementById('modeSelectionModal').style.display = 'none';
}

function updateModeUI()
{
    const button = document.getElementById('mode-action-button');
    if (button)
    {
        button.textContent = lobby_player.is_leader ? 'Changer le mode' : 'Prêt';
        button.onclick = lobby_player.is_leader ? openModeSelection : setReadyStatus;
    }
}

async function applyModeSelection()
{
    const data = {
        'match-choice': {
            'connect': document.getElementById('id_connect').value,
            'mode': document.getElementById('id_mode').value,
            'matchmaking': document.getElementById('id_mm').value
        }
    };
    const response = await APIRequest('/api/users/me/lobbies/main/', data, 'PATCH');
    if (response.ok)
    {
        closeModeSelection();
    }
}

function setReadyStatus()
{
    const button = document.getElementById('mode-action-button');
    if (button)
    {
        button.textContent = 'Annuler';
        button.style.backgroundColor = '#7f8c8d';
        button.style.color = '#fff';
        button.onclick = unsetReadyStatus;
        updatePlayerStatus('ready');
    }
}

function unsetReadyStatus()
{
    const button = document.getElementById('mode-action-button');
    if (button)
    {
        button.textContent = 'Prêt';
        button.style.backgroundColor = '#16a085';
        button.style.color = '#fff';
        button.onclick = setReadyStatus;
        updatePlayerStatus('not-ready');
    }
}

async function updatePlayerStatus(status)
{
    const friendStatus = document.querySelector('#lobbyPlayers .status');
    const statusText = status === 'ready' ? 'Prêt' : 'Pas prêt';
    
    if (friendStatus)
    {
        friendStatus.textContent = statusText;
        friendStatus.classList.toggle('ready', status === 'ready');
        friendStatus.classList.toggle('not-ready', status === 'not-ready');
    }

    const playerBannerStatus = document.querySelector('.lobby-players .player-status .status');
    if (playerBannerStatus)
    {
        playerBannerStatus.textContent = statusText;
        playerBannerStatus.classList.toggle('ready', status === 'ready');
        playerBannerStatus.classList.toggle('not-ready', status === 'not-ready');
    }
    const data = {
        is_ready: status === 'ready'
    };
    await APIRequest(`/api/users/me/lobbies/main/members/me/`, data, "PATCH");
}

async function enableNameEdit(element)
{
    const currentName = element.textContent;
    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentName;
    input.className = 'name-edit-input';
    input.id = 'name-edit-input';

    element.replaceWith(input);
    input.focus();

    input.addEventListener('keydown', (event) =>
    {
        if (event.key === 'Enter')
        {
            const newName = input.value.trim() || currentName;
            createPlayerNameElement(newName, input);
            const data = {
                pseudo: newName
            };
            await APIRequest(`/api/users/me/lobbies/main/members/me/`, data, "PATCH");
        }
    });

    input.addEventListener('blur', () =>
    {
        setTimeout(() => createPlayerNameElement(currentName, input), 100);
    });
}

function createPlayerNameElement(name, input)
{
    const span = document.createElement('div');
    span.className = 'player-name';
    span.id = 'player-name';
    span.textContent = name;
    span.onclick = () => enableNameEdit(span);
    input.replaceWith(span);
}

function filterFriends()
{
    const input = document.getElementById('friendSearch');
    const filter = input.value.toLowerCase();
    const friends = document.getElementById('friendList').getElementsByTagName('li');

    Array.from(friends).forEach(friend =>
    {
        const txtValue = (friend.textContent || friend.innerText).trim();
        friend.style.display = txtValue.toLowerCase().includes(filter) ? "" : "none";
    });
}

function closeMenu(menu)
{
    menu.style.display = 'none';
}

async function inviteToGroup(playerName)
{
    const data = {
        type: 'invite'
    };
    const response = await APIRequest(`/api/users/me/friends/${playerName}/lobby/requests/`, data, "POST");
    if (response.ok)
    {
        console.log("Invite request sent to: ", playerName);
    }
}

async function joinPlayerGroup(playerName)
{
    const data = {
        type: 'join'
    };
    const response = await APIRequest(`/api/users/me/friends/${playerName}/lobby/requests/`, data, "POST");
    if (response.ok)
    {
        console.log("Join request sent to: ", playerName);
    }
}

function toggleInviteMenu(inviteMenu)
{
    if (inviteMenu.classList.contains('active'))
    {
        closeInviteMenu(inviteMenu);
    }
    else
    {
        openInviteMenu(inviteMenu);
    }
}

function openInviteMenu(inviteMenu)
{
    const inviteButton = document.getElementById('inviteButton');
    inviteButton.style.display = 'none';
    inviteMenu.classList.add('active');
}

function closeInviteMenu(inviteMenu)
{
    inviteMenu.classList.remove('active');
    inviteButton.style.display = 'block';
}

function handleFriendClick(event, menu, selectedFriend)
{
    if (event.target.classList.contains('list-group-item'))
    {
        event.preventDefault();
        if (selectedFriend === event.target) // second click
        {
            closeMenu(menu);
            return null;
        }
        
        const rect = event.target.getBoundingClientRect();
        menu.style.display = 'block';
        menu.style.top = `${rect.bottom + window.scrollY}px`;
        menu.style.left = `${rect.left + window.scrollX}px`;
        selectedFriend = event.target;
        const selectedName = selectedFriend.getAttribute('data-username');

        document.getElementById('invite-group').onclick = () => { // inside click
            inviteToGroup(selectedName);
            closeMenu(menu);
            selectedFriend = null;
        };
        document.getElementById('join-group').onclick = () => { // inside click
            joinPlayerGroup(selectedName);
            closeMenu(menu);
            selectedFriend = null;
        };
    }
    return selectedFriend;
}

async function addFriend(userName)
{
    const response = await APIRequest(`/api/users/${userName}/requests/`, {}, "POST");
    if (response.ok)
    {
        console.log("Friend request sent to:", userName);
    }
}

async function acceptFriendRequest(friendName)
{
    const response = await APIRequest(`/api/users/me/requests/${friendName}/`, {}, "PUT");
    if (response.ok)
    {
        console.log("Friend request from ", friendName, " accepted");
    }
}

async function rejectFriendRequest(friendName)
{
    const response = await APIRequest(`/api/users/me/requests/${friendName}/`, {}, "DELETE");
    if (response.ok)
    {
        console.log("Friend request from ", friendName, " rejected");
    }
}

async function acceptLobbyRequest(requesterName, request_type)
{
    const data = {
        type: request_type
    };
    const response = await APIRequest(`/api/users/me/lobbies/main/requests/${requesterName}/`, data, "PUT");
    if (response.ok)
    {
        console.log(request_type, " request from ", requesterName, " accepted");
    }
}

async function rejectLobbyRequest(requesterName, request_type)
{
    const data = {
        type: request_type
    };
    const response = await APIRequest(`/api/users/me/lobbies/main/requests/${requesterName}/`, data, "DELETE");
    if (response.ok)
    {
        console.log(request_type, " request from ", requesterName, " accepted");
    }
}

document.addEventListener("DOMContentLoaded", async function () 
{
    await updateLobbyVar();
    console.log("Lobby: ", lobby)
    updateModeUI();
    initWebSocket();
    let selectedFriend = null;
    document.addEventListener('click', function(event)
    {
        const menu = document.getElementById('friend-actions-menu');
        const inviteMenu = document.getElementById('inviteMenu');
        const inviteButton = document.getElementById('inviteButton');
        if (event.target.id === 'toggle-online-button')
        {
            toggleSection("onlineFriends");
        }
        else if (event.target.id === 'toggle-offline-button')
        {
            toggleSection("offlineFriends");
        }
        else if (event.target.id === 'close-modal-button')
        {
            closeModeSelection();
        }
        else if (event.target.id === 'apply-mode-button')
        {
            applyModeSelection();
        }
        else if (event.target.id === 'editable-name')
        {
            enableNameEdit(event.target);
        }
        else if (event.target.id === 'inviteButton')
        {
            event.stopPropagation();
            toggleInviteMenu(inviteMenu);
        }
        else if (event.target.id === 'acceptFriendRequest')
        {
            const requesterName = document.getElementById('requesterName').textContent;
            acceptFriendRequest(requesterName);
        }
        else if (event.target.id === 'rejectFriendRequest')
        {
            const requesterName = document.getElementById('requesterName').textContent;
            rejectFriendRequest(requesterName);
        }
        else if (event.target.id === 'acceptLobbyRequest')
        {
            const requesterName = document.getElementById('lobbyRequesterName').textContent;
            const request = document.querySelector('span[data-request-type]');
            const requestType = request.getAttribute('data-request-type');
            acceptLobbyRequest(requesterName, requestType);
        }
        else if (event.target.id === 'rejectLobbyRequest')
        {
            const requesterName = document.getElementById('lobbyRequesterName').textContent;
            const request = document.querySelector('span[data-request-type]');
            const requestType = request.getAttribute('data-request-type');
            rejectLobbyRequest(requesterName, requestType);
        }
        else if (event.target.id === 'addFriendButton')
        {
            const addFriendInput = document.getElementById('addFriendInput');
            addFriend(addFriendInput.value);
        }
        else if (event.target.id === 'friendSearch')
        {
            const friendSearchInput = document.getElementById('friendSearch');
            friendSearchInput?.addEventListener('keyup', filterFriends);
        }
        else if (event.target.parentElement.id === 'onlineFriends')
        {
            selectedFriend = handleFriendClick(event, menu, selectedFriend)
        }
        else if (event.target.parentElement.id == 'offlineFriends')
        {
            selectedFriend = handleFriendClick(event, menu, selectedFriend)
        }
        if (!menu.contains(event.target) && !event.target.classList.contains('list-group-item')) // outside click
        {
            closeMenu(menu);
            selectedFriend = null;
        }
        if (inviteMenu && inviteButton && !inviteMenu.contains(event.target) && event.target !== inviteButton) // outside click
        {
            closeInviteMenu(inviteMenu);
        }
    });
});