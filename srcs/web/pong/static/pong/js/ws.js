const path = window.location.pathname;
const sessionId = path.split('/')[2];
const wsUrl = `/ws/pong/${sessionId}/`;

const canvas = document.getElementById("pongCanvas");
const ctx = canvas.getContext("2d");

const CANVAS_WIDTH_RATIO = 0.8;
const HEIGHT_GAP_RATIO = 0.1;
const CANVAS_BASE_WIDTH = 500;

let Utils = null;
let gameState = null;
let gameParams = null;

import(window.STATIC_VERSIONED_PATHS.utils)
    .then(async module => {
        Utils = module.default;
        await initGame();
    })
    .catch(error => console.error("Erreur lors du chargement de utils.js :", error));

async function pongWSHandler(event)
{
    const data = JSON.parse(event.data);
    if (data.state)
	{
        gameState = data.state;
        drawGame(gameState);
    }
}

async function handleKeyDown(event)
{
    if (event.repeat) 
        return;
    let response = null;
    switch (event.key.toLowerCase())
	{
        case "arrowup":
        case "z":
			response = await Utils.APIRequest(`/api/games/sessions/${sessionId}/state/`, {move: 'up'}, "PATCH");
			if (!response.ok) {
				console.error("Échec move up.");
			}
            break;
        case "arrowdown":
        case "s":
			response = await Utils.APIRequest(`/api/games/sessions/${sessionId}/state/`, {move: 'down'}, "PATCH");
			if (!response.ok) {
				console.error("Échec move down.");
			}
            break;
    }
}

async function handleKeyUp(event)
{
	const response = await Utils.APIRequest(`/api/games/sessions/${sessionId}/state/`, {move: null}, "PATCH"); 
	if (!response.ok) {
		console.error("Échec move reset.");
	}
}


async function initGame()
{
    try
	{
        await Utils.initWS('pong', wsUrl, pongWSHandler);

        const response = await Utils.APIRequest(`/api/games/sessions/${sessionId}/`);
        if (!response.ok) {
            console.error("Échec de récupération de la session de jeu.");
            return;
        }

        gameParams = response.session.parameters;
        gameState = response.state;

        canvas.width = CANVAS_BASE_WIDTH;
        canvas.height = CANVAS_BASE_WIDTH / 2;

        const startResponse = await Utils.APIRequest(`/api/games/sessions/${sessionId}/`, {}, "PUT");
        if (!startResponse.ok) {
            console.error("Échec du démarrage de la partie.");
        }
		document.addEventListener("keydown", handleKeyDown);
		document.addEventListener("keyup", handleKeyUp);

    }
	catch (error) {
        console.error("Erreur lors de l'initialisation du jeu :", error);
    }
}

function drawGame(state)
{
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const fieldWidth = canvas.width * CANVAS_WIDTH_RATIO;
    const fieldHeight = fieldWidth * gameParams.field_ratio;
    const fieldX = (canvas.width - fieldWidth) / 2;
    const fieldY = (canvas.height + canvas.height * HEIGHT_GAP_RATIO - fieldHeight) / 2;

    // Terrain
    ctx.strokeStyle = "white";
    ctx.lineWidth = 2;
    ctx.strokeRect(fieldX, fieldY, fieldWidth, fieldHeight);

    // Balle
    const ball = {
        x: fieldX + state.ball.coordinate_x * fieldWidth,
        y: fieldY + state.ball.coordinate_y * fieldWidth,
        radius: gameParams.ball_radius * fieldWidth
    };

    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fillStyle = "red";
    ctx.fill();

    // Paddles
    ctx.font = "20px Arial";
    ctx.fillStyle = "white";

    state.teams.forEach((team, index) => {
        const scoreX = index === 0 ? canvas.width / 4 : (3 * canvas.width) / 4;
        ctx.fillText(team.score, scoreX, 30);

        team.players.forEach(player => {
            const paddle = {
                x: fieldX + player.coordinate_x * fieldWidth,
                y: fieldY + player.coordinate_y * fieldWidth,
                width: gameParams.paddle_width * fieldWidth,
                height: team.paddle_length * fieldWidth
            };
            ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);
        });
    });
}
