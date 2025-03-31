const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

async function initWS(name, url, eventHandler = null)
{
	return new Promise((resolve, reject) => {
		try
		{
			const ws = new WebSocket(url);

			ws.onopen = function ()
			{
				console.log(`WebSocket connection ${name} opened successfully.`);
				resolve(ws); 
			};
			ws.onmessage = async function (event)
			{
				try
				{
					if (eventHandler) {
						eventHandler(event);
					}
					else {
						console.log(event);
					}
				}
				catch (error) {
					console.error(`Error handling WebSocket ${name} message: `, event.data, error);
				}
			};
			ws.onerror = function (error)
			{
				console.error("WebSocket error observed: ", error);
				reject(error);
			};
			ws.onclose = async function (event)
			{
				if (event.wasClean) 
				{
					console.log(`WebSocket connection ${name} closed cleanly.`);
					console.error("Code:", event.code);
					if (event.reason) {
						console.error("Reason:", event.reason);
					}
				}
				else
				{
					console.error(`WebSocket connection ${name} closed unexpectedly.`);
					console.error("Code:", event.code);
					if (event.reason) {
						console.error("Reason:", event.reason);
					}
				}
			};
		}
		catch (error)
		{
			console.error(`Failed to initialize WebSocket ${name} : ${error}`);
			reject(error);
		}
	});
}


async function APIRequest(url, data = null, http_method = 'GET')
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

		if (data && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(http_method))
		{
			options.body = JSON.stringify(data);
		}

		response = await fetch(url, options);

		const textResponse = await response.text();
		if (textResponse)
		{
			try {
				jsonResponse = JSON.parse(textResponse);
			}
			catch (parseError) {
				console.error(`[APIRequest] Réponse invalide (non-JSON) :`, textResponse);
			}
		}

		if (!response.ok)
		{
			if (jsonResponse?.errors)
			{
				for (const [key, message] of Object.entries(jsonResponse.errors)) {
					console.error(`[APIRequest] Erreur (${key}): ${message}`);
				}
			}
			else if (response.status === 303 && jsonResponse?.match?.url)
			{
				console.log("Redirection...");
				window.location.href = jsonResponse.match.url;
			}
			else {
				console.error(`[APIRequest] Erreur HTTP ${response.status} : ${response.statusText}`);
			}
		}

		if (jsonResponse?.message) {
			console.log("Message from API:", jsonResponse.message);
		}
	} 
	catch (error) {
		console.error('[APIRequest] Erreur lors de la requête:', error);
	}

	return {
		ok: response?.ok ?? false,
		status: response?.status ?? undefined,
		...(jsonResponse || {}),
	};
}


export default {
	initWS,
	APIRequest
  };