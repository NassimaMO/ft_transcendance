let isGroupLeader = false;

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
        button.textContent = isGroupLeader ? 'Changer le mode' : 'Prêt';
        button.onclick = isGroupLeader ? openModeSelection : setReadyStatus;
    }
}

function applyModeSelection()
{
    const connectivity = document.getElementById('connectivity').value;
    const mode = document.getElementById('mode').value;
    const matchmaking = document.getElementById('matchmaking').value;

    document.getElementById('connectivity-status').textContent = connectivity;
    document.getElementById('game-mode').textContent = mode;
    document.getElementById('matchmaking-status').textContent = matchmaking;
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
        const txtValue = friend.textContent || friend.innerText;
        friend.style.display = txtValue.toLowerCase().includes(filter) ? "" : "none";
    });
}

function closeMenu(menu)
{
    menu.style.display = 'none';
}

function inviteToGroup(player)
{
    const playerName = player.textContent.trim()
}

function joinPlayerGroup(player)
{
    const playerName = player.textContent.trim()
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

document.addEventListener("DOMContentLoaded", function ()
{
    const elements = {
        toggleOnlineButton: document.getElementById('toggle-online-button'),
        toggleOfflineButton: document.getElementById('toggle-offline-button'),
        closeModalButton: document.getElementById('close-modal-button'),
        applyButton: document.getElementById('apply-mode-button'),
        playerName: document.getElementById('editable-name'),
        friendSearchInput: document.getElementById('friendSearch'),
        inviteButton: document.getElementById('inviteButton'),
        inviteMenu: document.getElementById('inviteMenu'),
        menu: document.getElementById('friend-actions-menu'),
        friendItems: document.querySelectorAll('.list-group-item'),
        prevRequest: document.getElementById('prevRequest'),
        nextRequest: document.getElementById('nextRequest'),
        acceptRequest: document.getElementById('acceptRequest'),
        rejectRequest: document.getElementById('rejectRequest'),
        addFriendButton: document.getElementById('addFriendButton'),
        addFriendInput: document.getElementById('addFriendInput')
    };

    if (elements.toggleOnlineButton)
    {
        elements.toggleOnlineButton.addEventListener('click', () => toggleSection("onlineFriends"));
    }

    if (elements.toggleOfflineButton)
    {
        elements.toggleOfflineButton.addEventListener('click', () => toggleSection("offlineFriends"));
    }

    if (elements.closeModalButton)
    {
        elements.closeModalButton.addEventListener('click', closeModeSelection);
    }

    if (elements.applyButton)
    {
        elements.applyButton.addEventListener('click', applyModeSelection);
    }

    if (elements.playerName)
    {
        elements.playerName.addEventListener('click', () => enableNameEdit(elements.playerName));
    }

    if (elements.friendSearchInput)
    {
        elements.friendSearchInput.addEventListener('keyup', filterFriends);
    }

    if (elements.inviteButton)
    {
        elements.inviteButton.addEventListener('click', (event) =>
        {
            event.stopPropagation();
            toggleInviteMenu(elements.inviteMenu);
        });
    }

    document.addEventListener('click', function(event)
    {
        const isClickInsideMenu = inviteMenu.contains(event.target);
        const isClickOnInviteButton = inviteButton.contains(event.target);
    
        if (!isClickInsideMenu && !isClickOnInviteButton)
        {
            closeInviteMenu(inviteMenu);
        }
    });

    let selectedFriend = null;

elements.friendItems.forEach(friend =>
{
    friend.addEventListener('click', function(event)
    {
        event.preventDefault();

        if (selectedFriend === friend)
        {
            closeMenu(elements.menu);
            selectedFriend = null;
        } 
        else
        {
            const rect = friend.getBoundingClientRect();
            elements.menu.style.display = 'block';
            elements.menu.style.top = `${rect.bottom + window.scrollY}px`;
            elements.menu.style.left = `${rect.left + window.scrollX}px`;

            selectedFriend = friend;

            document.getElementById('invite-group').onclick = () =>
            {
                inviteToGroup(selectedFriend);
                closeMenu(elements.menu);
                selectedFriend = null;
            };
            document.getElementById('join-group').onclick = () =>
            {
                joinPlayerGroup(selectedFriend);
                closeMenu(elements.menu);
                selectedFriend = null;
            };
        }
    });
});


    document.addEventListener('click', (event) =>
    {
        if (!elements.menu.contains(event.target) && !event.target.classList.contains('list-group-item'))
        {
            closeMenu(elements.menu);
        }
    });
});

window.onload = updateModeUI;
