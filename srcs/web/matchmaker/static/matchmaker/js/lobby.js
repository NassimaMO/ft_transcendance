let lobby = null
let lobby_player = null
const protocol = window.location.protocol === 'http:' ? 'ws://' : 'wss://';
const port = window.location.protocol === 'http:' ? '8000' : '443';
let ws = null

async function updateLobbyVar()
{
    try
    {
        const response = await fetch(`/lobby/${lobbyId}/get`);
        const data = await response.json();
        lobby = data.lobby;
        lobby_player = lobby.players[0];
        // console.log("Lobby data updated: ", lobby);
    }
    catch (error)
    {
        console.error("Failed to fetch lobby data:", error);
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

function applyModeSelection()
{
    const connectivity = document.getElementById('id_connect').value;
    const mode = document.getElementById('id_mode').value;
    const matchmaking = document.getElementById('id_mm').value;
    console.log(connectivity)

    document.getElementById('default_id_connect').textContent = connectivity;
    document.getElementById('default_id_mode').textContent = mode;
    document.getElementById('default_id_mm').textContent = matchmaking;
    closeModeSelection();
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

function updatePlayerStatus(status)
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
}

function enableNameEdit(element)
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

function inviteToGroup(playerName)
{
    const message = {
        "request": "invite",
        "recipient": playerName
    };

    ws.send(JSON.stringify(message));
    console.log("Invitation sent to:", playerName);
}

function joinPlayerGroup(playerName)
{
    const message = {
        "request": "join",
        "recipient": playerName
    };

    ws.send(JSON.stringify(message));
    console.log("Request to join group sent to:", playerName);
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

function addFriend(friendName)
{
    const message = {
        "request": "friend",
        "recipient": friendName
    };
    ws.send(JSON.stringify(message));
    console.log("Friend request sent to:", friendName);
}

function acceptRequest(friendName)
{
    const message = {
        "accept": "friend",
        "username": friendName
    };
    ws.send(JSON.stringify(message));
    console.log("Friend request from ", friendName, " accepted");
}

function rejectRequest(friendName)
{
    const message = {
        "reject": "friend",
        "username": friendName
    };
    ws.send(JSON.stringify(message));
    console.log("Friend request from ", friendName, " rejected");
}

function acceptLobbyRequest(requesterName, type)
{
    const message = {
        "accept": type,
        "username": requesterName
    };
    ws.send(JSON.stringify(message));
    console.log(type, " request from ", requesterName, " accepted");
}

function rejectLobbyRequest(requesterName, type)
{
    const message = {
        "reject": type,
        "username": requesterName
    };
    ws.send(JSON.stringify(message));
    console.log(type, " request from ", requesterName, " accepted");
}

async function initWebSocket()
{
    ws = new WebSocket(`${protocol}//${window.location.hostname}:${port}/ws/lobby`);
    ws.onmessage = async function(event)
    {
        const data = JSON.parse(event.data);
        console.log("received data : ", data)
        if (data.type == "notif")
        {
            await updateLobbyVar();
            switch (data.change)
            {
                case "join":
                    updateSection('lobby-list')
                    updateSection('lobby-players')
                    console.log(data.username, " joined the lobby");
                    break;
                case "leave":
                    updateSection('lobby-list')
                    updateSection('lobby-players')
                    console.log(data.username, " left the lobby");
                    break;
                case "new-lobby":
                    updateSection('lobby-list')
                    updateSection('lobby-players')
                    updateSection('lobby-modes')
                    console.log("You have joined the lobby");
                    break;
                case "friend-request":
                    updateSection("friend-requests")
                    break;
                case "friend" :
                    updateSection("friends-list")
                    updateSection("invite-banner")
                    break;
                case "lobby-request" :
                    updateSection("lobby-requests")
                    if (data.username)
                    {
                        console.log("New lobby request received from ", data.username)
                    }
                    else
                    {
                        console.log("Lobby request changes")
                    }
                    break;
                default:
                    console.log(data);
            }
        }
    };
}

function updateSection(section)
{
    let url = null;
    if (section === 'lobby-modes')
    {
        url = '/lobby/modes';
    }
    else if (section === 'lobby-players')
    {
        url = '/lobby/players';
    }
    else if (section === 'friend-requests')
    {
        url = '/lobby/requests/friends';
    }
    else if (section === 'lobby-requests')
    {
        url = '/lobby/requests/lobby';
    }
    else if (section === 'friends-list')
    {
        url = '/lobby/list/friends';
    }
    else if (section === 'lobby-list')
    {
        url = '/lobby/list';
    }
    else if (section === 'invite-banner')
    {
        url = '/lobby/invite_banner';
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

document.addEventListener("DOMContentLoaded", async function () 
{
    await updateLobbyVar();
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
        else if (event.target.id === 'acceptRequest')
        {
            const requesterName = document.getElementById('requesterName').textContent;
            acceptRequest(requesterName);
        }
        else if (event.target.id === 'rejectRequest')
        {
            const requesterName = document.getElementById('requesterName').textContent;
            rejectRequest(requesterName);
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