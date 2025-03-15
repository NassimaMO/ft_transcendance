const path = window.location.pathname;
const id = path.split('/')[2];
const url = `/ws/pong/${id}/`
let Utils = null;
let initial_state = null;
let parameters = null;
let ball = null;
const canvas = document.getElementById("pongCanvas");
const ctx = canvas.getContext("2d");
const width_ratio = 0.8;
const height_gap_ratio = 0.1;

import(window.STATIC_VERSIONED_PATHS.utils)
    .then(async module => {
        Utils = module.default;
        await main();
    })
    .catch(error => console.error("Erreur lors du chargement de utils.js :", error));


async function pongWSHandler(event)
{
	const data = JSON.parse(event.data);
	draw(data.state);
}

function draw(state)
{
	ctx.clearRect(0, 0, canvas.width, canvas.height);

	const width = canvas.width * width_ratio
	const height = width * parameters.field_ratio
	const x = canvas.width * (1 - width_ratio) / 2;
	const y = (canvas.height + canvas.height * height_gap_ratio - height) / 2

	const field = {x: x, y: y, width: width, height: height};
	ball = {x: field.x + state.ball.coordinate_x * field.width,
			y: field.y + state.ball.coordinate_y * field.width,
			radius: parameters.ball_radius * field.width}
	// console.log(state.ball)

	// Terrain
	ctx.strokeStyle = "white";
	ctx.lineWidth = 2;
	ctx.strokeRect(field.x, field.y, field.width, field.height);

	// Balle
	ctx.beginPath();
	ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
	ctx.fillStyle = "red";
	ctx.fill();

	// Scores
	ctx.font = "20px Arial";
	state.teams.forEach((team, index) => {
		let xPos = index === 0 ? canvas.width / 4 : (3 * canvas.width) / 4;
		ctx.fillText(team.score, xPos, 30);

		// Paddles
		team.players.forEach(player => {
			let paddle = {x: field.x + player.coordinate_x * field.width, y: field.y + player.coordinate_y * field.width, 
					width: parameters.paddle_width * field.width, height: team.paddle_length * field.width}
			ctx.fillStyle = "white";
			ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);
		});
	});
}

async function main()
{
	await Utils.initWS('pong', url, pongWSHandler);
	let response = await Utils.APIRequest(`/api/games/sessions/${id}/`);
	if (response.ok)
	{
		const state = response.state;
		parameters = response.session.parameters;
		canvas.width = 500;
		canvas.height = canvas.width / 2;
		response = await Utils.APIRequest(`/api/games/sessions/${id}/`, {}, "PUT");
		if (!response.ok) {
			console.error("Failed to start game");
		}
	}
	else {
		console.error("Failed to fetch session data");
	}
}
