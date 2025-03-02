const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

async function initWS(name, url, eventHandler = null)
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
				if (eventHandler) {
					eventHandler(event)
				}
				else {
					console.log(event)
				}
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
			else if (response.status == 303)
			{
				console.log("Redirection...");
				window.location.href = jsonResponse.match.url;
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

export default {
	initWS,
	APIRequest
  };