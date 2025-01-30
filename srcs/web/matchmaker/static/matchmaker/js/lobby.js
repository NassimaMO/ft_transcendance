let lobby_player = null
let lobby = null
const protocol = window.location.protocol === 'http:' ? 'ws://' : 'wss://';
const port = window.location.protocol === 'http:' ? '8000' : '443';
const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

async function APIRequest(url, data=null, http_method='GET')
{
	let response = null;
	let jsonResponse = null;
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
		if (data && (http_method === 'POST' || http_method === 'PUT' || http_method === 'PATCH' || http_method === 'DELETE')) {
			options.body = JSON.stringify(data);
		}
		response = await fetch(url, options); 
		jsonResponse = await response.json();
		if (!response.ok)
		{
			if (jsonResponse.errors)
			{
				for (const [key, message] of Object.entries(jsonResponse.errors)) {
					console.error(`[APIRequest] Erreur (${key}): ${message}`);
				}
			}
			else {
				console.error('[APIRequest] Une erreur inattendue est survenue.');
			}
		}
		if (jsonResponse.message) {
			console.log("Message from API : ", jsonResponse.message);
		}
	}
	catch (error) {
		console.error('[APIRequest] Erreur lors de la requête:', error);
	}
	if (jsonResponse) {
		return {ok: response.ok, status: response.status, ...jsonResponse};
	}
	if (response) {
		return {ok: response.ok, status: response.status};
	}
	return {ok: false, status: undefined};
}

async function updateVars()
{
	try
	{
		const response = await APIRequest('/api/lobbies/main/');
		if (response.ok) {
			lobby = response.lobby
			lobby_player = response.lobby.members[0];
		}
		else {
			console.error("Failed to fetch lobby data");
		}
	}
	catch (error) {
		console.error("Failed to fetch lobby data:", error);
	}
}

async function initWS(name, url, eventHandler)
{
	try
	{
		const ws = new WebSocket(url);
		ws.onopen = function() {
			console.log(`WebSocket connection ${name} opened successfully.`);
		};
		
		ws.onmessage = async function(event)
		{
			try {
				await updateVars();
				eventHandler(event)
			}
			catch (error) {
				console.error(`Error handling WebSocket ${name} message: `, event.data, error);
			}
		};

		ws.onerror = function(error) {
			console.error("WebSocket error observed: ", error);
		};

		ws.onclose = async function(event)
		{
			if (event.wasClean)
			{
				console.log(`WebSocket connection ${name} closed cleanly.`);
				console.error("Code:", event.code);
				if (event.reason) {
					console.error("Reason:", event.reason)
				}
			}
			else
			{
				console.error(`WebSocket connection ${name} closed unexpectedly.`);
				console.error("Code:", event.code);
				if (event.reason) {
					console.error("Reason:", event.reason)
				}
				
			}
		};
	}
	catch (error) {
		console.error(`Failed to initialize WebSocket ${name} : ${error}`);
	}
}

async function matchmakingWSHandler(event)
{
	const data = JSON.parse(event.data);
	console.log("Received mm handler: ", data.type);
	if (data.type === "queue_start") {
		updateTimerStart();
	}
	else if (data.type === "queue_stop") {
		updateTimerStop();
	}
	else if (data.type === "match_found")
	{
		updateTimerStop();
		matchFound(data.match_url);
	}
}

async function lobbyWSHandler(event)
{
	const data = JSON.parse(event.data);
	if (data.type === "notif")
	{
		for (const change of data.changes)
		{
			switch (change.type)
			{
				case "join":
					updateSection('lobby-list');
					updateSection('lobby-players');
					updateSection('matchmaking');
					if (change.username == lobby_player.user.username) {
						console.log("You joined the lobby");
					}
					else if (change.username){
						console.log(change.username, "joined the lobby");
					}
					else {
						console.log("A player joined the lobby");
					}
					break;
				case "leave":
					updateSection('lobby-list');
					updateSection('lobby-players');
					updateSection('matchmaking');
					if (change.username == lobby_player.user.username) {
						console.log("You left the lobby");
					}
					else if (change.username) {
						console.log(change.username, "left the lobby");
					}
					else {
						console.log("A player left the lobby");
					}
					break;
				case "lobby":
					updateSection('lobby-list');
					updateSection('lobby-players');
					updateSection('lobby-modes');
					updateSection('matchmaking');
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
					if (change.username) {
						console.log("New lobby request received from ", change.username);
					}
					break;
				case "match-choice":
					updateSection("lobby-modes");
					break;
				case "player":
					updateSection('lobby-players');
					updateSection('lobby-list');
					updateSection('lobby-modes');
					updateSection('matchmaking');
					break;
				case "user":
					updateSection('lobby-players');
					updateSection('lobby-list');
					updateSection("invite-banner");
					break;
				default:
					console.log("Unhandled change:", change.type);
			}
		}
	}
}

function updateSection(section)
{
	let url = null;

	if (section === 'lobby-modes') {
		url = '/lobby/modes/';
	}
	else if (section === 'lobby-players') {
		url = '/lobby/players/';
	}
	else if (section === 'friend-requests') {
		url = '/lobby/requests/friends/';
	}
	else if (section === 'lobby-requests') {
		url = '/lobby/requests/lobby/';
	}
	else if (section === 'friends-list') {
		url = '/lobby/list/friends/';
	}
	else if (section === 'lobby-list') {
		url = '/lobby/list/';
	}
	else if (section === 'invite-banner') {
		url = '/lobby/invite_banner/';
	}
	else if (section == "matchmaking") {
		url = "/lobby/matchmaking/"
	}
	if (url)
	{
		fetch(url)
			.then(response => response.text())
			.then(html => {
				document.getElementById(`${section}`).innerHTML = html;
			})
			.catch(error => console.error('Erreur de mise à jour de la section:', error));
	}
	else  {
		console.error('Erreur de mise à jour de la section: url indisponible')
	}
}

function redirectToGame(url) {
    window.location.href = url;
}

function showMatchFound(url) {
    const overlay = document.getElementById('match-found-overlay');
    const countdownText = document.getElementById('countdown-text');
    overlay.style.display = 'flex';

    let countdown = 3;
    countdownText.textContent = countdown;

    const countdownInterval = setInterval(() => {
        countdown -= 1;
        countdownText.textContent = countdown;

        if (countdown === 0)
		{
            clearInterval(countdownInterval);
            redirectToGame(url);
        }
    }, 1000);
}

let timerInterval = null;

function formatTime(seconds)
{
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}

// function updateUIMatchmakingAvailable()
// {
// 	const button = document.getElementById('matchmaking-btn');
// 	if (!lobby.members.every(player => player.is_ready))
// 	{
// 		button.setAttribute("title", "Tous les joueurs ne sont pas prêts.");
// 		button.classList.add('btn-grayed-out');
// 		button.classList.add('btn-disabled');
// 	}
// 	else
// 	{
// 		button.removeAttribute('title');
// 		button.classList.remove('btn-disabled');
// 		button.classList.remove('btn-grayed-out');
// 	}
// }

function updateTimerStart()
{
	const button = document.getElementById('matchmaking-btn');
	timerInterval = setInterval(() => {
		const seconds = Math.floor((Date.now() - lobby.queue_start * 1000) / 1000);
		button.textContent = formatTime(seconds);
	}, 1000);
}

function updateTimerStop()
{
	const button = document.getElementById('matchmaking-btn');
	button.textContent = "JOUER";
	if (timerInterval) {
		clearInterval(timerInterval);
	}
}

function updateUIMatchmaking()
{
	if (lobby.is_in_queue) {
		updateTimerStart();
	}
	else {
		updateTimerStop();
	}
}

async function startMatchmaking()
{
	const data = {
		is_in_queue: true
	};
	const response = await APIRequest("/api/lobbies/main/", data, "PATCH");
	if (response.ok) {
		console.log('Matchmaking started');
	}
	else {
		console.error('Erreur de lancement du matchmaking');
	}
}

async function stopMatchmaking()
{
	const data = {
		is_in_queue: false
	};
	const response = await APIRequest("/api/lobbies/main/", data, "PATCH");
	if (response.ok)
	{
		updateTimerStop();
		console.log('Matchmaking stopped');
	}
	else
	{
		console.error('Erreur de lancement du matchmaking');
	}
}

function matchFound(url) {
	clearInterval(timerInterval);
    showMatchFound(url);
}

function toggleSection(sectionId)
{
	const section = document.getElementById(sectionId);
	if (section) {
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

async function applyModeSelection()
{
	const data = {
		'match-choice': {
			'connectivity': document.getElementById('id_connectivity').value,
			'mode': document.getElementById('id_mode').value,
			'matchmaking': document.getElementById('id_matchmaking').value
		}
	};
	const response = await APIRequest('/api/lobbies/main/', data, 'PATCH');
	if (response.ok) {
		closeModeSelection();
	}
}

async function setReadyStatus()
{
	const button = document.getElementById('mode-action-button');
	if (button)
	{
		button.textContent = 'Annuler';
		button.style.backgroundColor = '#7f8c8d';
		button.style.color = '#fff';
		await updatePlayerStatus('ready');
	}
}

async function unsetReadyStatus()
{
	const button = document.getElementById('mode-action-button');
	if (button)
	{
		button.textContent = 'Prêt';
		button.style.backgroundColor = '#16a085';
		button.style.color = '#fff';
		await updatePlayerStatus('not-ready');
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
	await APIRequest(`/api/players/me/`, data, "PATCH");
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

	input.addEventListener('keydown', async (event) =>
	{
		if (event.key === 'Enter')
		{
			const newName = input.value.trim() || currentName;
			createPlayerNameElement(newName, input);
			const data = {
				pseudo: newName
			};
			await APIRequest(`/api/players/me/`, data, "PATCH");
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
	const response = await APIRequest(`/api/players/${playerName}/requests/`, data, "POST");
	if (response.ok){
		console.log("Invite request sent to: ", playerName);
	}
	else {
		console.log(`Error inviting ${playerName}: can't send request.`);
	}
}

async function joinPlayerGroup(playerName)
{
	const data = {
		type: 'join'
	};
	const response = await APIRequest(`/api/players/${playerName}/requests/`, data, "POST");
	if (response.ok){
		console.log("Invite request sent to ", playerName);
	}
	else {
		console.log(`Error joining ${playerName}: can't send request.`);
	}
}

function toggleInviteMenu(inviteMenu)
{
	if (inviteMenu.classList.contains('active')) {
		closeInviteMenu(inviteMenu);
	}
	else {
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
	if (response.ok) {
		console.log("Friend request sent to:", userName);
	}
}

async function acceptFriendRequest(friendName)
{
	const response = await APIRequest(`/api/users/me/requests/${friendName}/`, {}, "PUT");
	if (response.ok) {
		console.log("Friend request from ", friendName, " accepted");
	}
}

async function rejectFriendRequest(friendName)
{
	await APIRequest(`/api/users/me/requests/${friendName}/`, {}, "DELETE");
}

async function acceptLobbyRequest(requestId)
{
	await APIRequest(`/api/players/me/requests/${requestId}/`, {}, "PUT");
}

async function rejectLobbyRequest(requestId)
{
	await APIRequest(`/api/players/me/requests/${requestId}/`, {}, "DELETE");
}

async function leaveLobby()
{
	await APIRequest('/api/lobbies/main/', {}, "PUT");
}

document.addEventListener("DOMContentLoaded", async function () 
{
	await updateVars();
	updateUIMatchmaking();
	await initWS("lobby", `${protocol}//${window.location.hostname}:${port}/ws/lobby`, lobbyWSHandler);
	await initWS("matchmaking", `${protocol}//${window.location.hostname}:${port}/ws/matchmaking`, matchmakingWSHandler);
	let selectedFriend = null;
	document.addEventListener('click', async function(event)
	{
		const menu = document.getElementById('friend-actions-menu');
		const inviteMenu = document.getElementById('inviteMenu');
		const inviteButton = document.getElementById('inviteButton');

		if (event.target.id == "button-lobby" || event.target.id == "button-carreer")
		{
			const buttons = document.querySelectorAll('.nav-button');

			buttons.forEach(btn => {
				btn.classList.remove('active');
			});
			event.target.classList.add('active');
		}
		if (event.target.id === 'matchmaking-btn' && lobby_player.is_leader)
		{
			if (lobby.is_in_queue === false && lobby.members.every(player => player.is_ready)) {
				startMatchmaking();
			}
			else {
				stopMatchmaking();
			}
		}
		else if (event.target.id === 'leaveLobbyButton') {
			leaveLobby();
		}
		else if (event.target.id === 'toggle-online-button') {
			toggleSection("onlineFriends");
		}
		else if (event.target.id === 'toggle-offline-button') {
			toggleSection("offlineFriends");
		}
		else if (event.target.id === 'close-modal-button') {
			closeModeSelection();
		}
		else if (event.target.id === 'mode-action-button')
		{
			if (lobby_player.is_leader) {
				openModeSelection();
			}
			else if (lobby_player.is_ready) {
				await unsetReadyStatus();
			}
			else {
				await setReadyStatus();
			}
		}
		else if (event.target.id === 'apply-mode-button') {
			applyModeSelection();
		}
		else if (event.target.id === 'editable-name') {
			enableNameEdit(event.target);
		}
		else if (event.target.id === 'inviteButton') {
			event.stopPropagation();
			toggleInviteMenu(inviteMenu);
		}
		else if (event.target.id === 'acceptFriendRequest')
		{
			const requesterName = document.getElementById('requesterName').textContent;
			await acceptFriendRequest(requesterName);
		}
		else if (event.target.id === 'rejectFriendRequest')
		{
			const requesterName = document.getElementById('requesterName').textContent;
			await rejectFriendRequest(requesterName);
		}
		else if (event.target.id === 'acceptLobbyRequest')
		{
			// const requesterName = document.getElementById('lobbyRequesterName').textContent;
			// const requestType = request.getAttribute('data-request-type');
			const request = document.querySelector('span[data-request-type]');
			const requestId = request.getAttribute('data-request-id');
			await acceptLobbyRequest(requestId);
		}
		else if (event.target.id === 'rejectLobbyRequest')
		{
			// const requesterName = document.getElementById('lobbyRequesterName').textContent;
			// const requestType = request.getAttribute('data-request-type');
			const request = document.querySelector('span[data-request-type]');
			const requestId = request.getAttribute('data-request-id');
			await rejectLobbyRequest(requestId);
		}
		else if (event.target.id === 'addFriendButton')
		{
			const addFriendInput = document.getElementById('addFriendInput');
			await addFriend(addFriendInput.value);
		}
		else if (event.target.id === 'friendSearch')
		{
			const friendSearchInput = document.getElementById('friendSearch');
			friendSearchInput?.addEventListener('keyup', filterFriends);
		}
		else if (event.target.parentElement && event.target.parentElement.id === 'onlineFriends') {
			selectedFriend = handleFriendClick(event, menu, selectedFriend)
		}
		// else if (event.target.parentElement && event.target.parentElement.id === 'offlineFriends') {
		//     selectedFriend = handleFriendClick(event, menu, selectedFriend)
		// }
		if (!menu.contains(event.target) && !event.target.classList.contains('list-group-item')) // outside click
		{
			closeMenu(menu);
			selectedFriend = null;
		}
		if (inviteMenu && inviteButton && !inviteMenu.contains(event.target) && event.target !== inviteButton) { // outside click
			closeInviteMenu(inviteMenu);
		}
	});
	const inputField = document.getElementById("addFriendInput");
    // const addButton = document.getElementById("addFriendButton");
	document.addEventListener('keydown', async function(event) {
		if (event.key === "Enter")
		{
			event.preventDefault();
			const value = inputField.value.trim();

			if (event.key === "Enter")
			{
				if (value)
				{
					event.preventDefault();
					addFriend(value);
				}
				else
				{
					// inputField.placeHolder = "Veuillez entrer un nom valide"
				}
            }

		}
	});
});
