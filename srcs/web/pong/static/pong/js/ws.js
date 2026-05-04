const path = window.location.pathname;
const session_id = path.split('/')[2];
const ws_url = `/ws/pong/${session_id}/`;

const canvas = document.getElementById("pongCanvas");
const ctx = canvas.getContext("2d");

const CANVAS_WIDTH_RATIO = 0.8;
const HEIGHT_GAP_RATIO = 0.1;
const CANVAS_BASE_WIDTH = 500;

let Utils = null;
let state = null;
let params = null;
let match = null;
let player_session = null;
const user_id = document.getElementById("config").dataset.userId;
console.log(user_id)
const keys_state = {};
let colors = ['blue', 'red']

import(window.STATIC_VERSIONED_PATHS.utils)
    .then(async module => {
        Utils = module.default;
        await initGame();
    })
    .catch(error => console.error("Erreur lors du chargement de utils.js :", error));

function printWinner2D(text, color)
{
    ctx.textAlign = "center";
    ctx.fillStyle = color;
    ctx.fillText(text, canvas.width / 2, 30);
}

function getEndgameText(winner_id)
{
    let text = "";
    let color = "white";
    

    for (const [index, team] of state.teams.entries())
    {
        if (team.id == winner_id)
        {
            if (match.info.connectivity == "Local" && match.info.mode != "Solo")
            {
                color = colors[index];
                text = `${colors[index].toUpperCase()} WON !`;
            }
            else
            {
                color = "red";
                text = "DEFEAT";
                for (const player of team.players)
                {
                    if (player.user && player.user.id == user_id)
                    {
                        color = "green";
                        text = "VICTORY";
                        break;
                    }
                }
            }
            return {text: text, color: color};
        }
    }
    color = "white";
    text = "DRAW";
    return {text: text, color: color}
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function pongWSHandler(event)
{
    const data = JSON.parse(event.data);
    if (data.type === "game_end")
    {
        const endgame_data = getEndgameText(data.winner);
        console.log(endgame_data);
        printWinner2D(endgame_data.text, endgame_data.color);
        await sleep(3000);
        window.location.href = data.url;
    }
    if (data.state)
	{
        state = data.state;
        engine2D(state);
    }
}

function getInputs()
{
    const inputs = {};

    inputs[state.teams[0].players[0].id] = { up: ['z'], down: ['s'] };
    if (match.info.connectivity === "Local" && match.info.mode === "1v1")
    {
        inputs[state.teams[1].players[0].id] = {up: ['p', 'arrowup'], down: ['l', 'arrowdown']};
    }
    if (match.info.connectivity === "Local" && match.info.mode === "2v2")
    {
        inputs[state.teams[0].players[1].id] = {up: ['f'], down: ['v']};
        inputs[state.teams[1].players[1].id] = {up: ['j'], down: ['n']};
        inputs[state.teams[1].players[0].id] = {up: ['p'], down: ['l']};
    }
    if (match.info.connectivity !== "Local" || match.info.mode === "Solo")
    {
        inputs[state.teams[0].players[0].id].up.push('arrowup');
        inputs[state.teams[0].players[0].id].down.push('arrowdown');
    }
    return inputs;
}

function checkInput(event)
{
    const inputs = getInputs();
    const key = event.key.toLowerCase();

    for (const player_id in inputs)
    {
        for (const move in inputs[player_id])
        {
            if (inputs[player_id][move].includes(key))
            {
                return { player_id: player_id, move: move };
            }
        }
    }
    return null;
}

async function handleKeyDown(event)
{
    const key = event.key.toLowerCase();
    const check = checkInput(event);
    // const opposite_keys = getOppositeKeys(key);

    if (keys_state[key])
        return;
    keys_state[key] = true;
    // if (opposite_keys)
    // {
    //     for (const input of opposite_keys.inputs)
    //     {
    //         if (keys_state[input])
    //         {
    //             const response = await Utils.APIRequest(`/api/games/sessions/${session_id}/state/players/${check.player_id}/`, 
    //                 {move: null}, 
    //                 "PATCH"); 
    //             if (!response.ok) {
    //                 console.error("ERROR handleKeyUp.");
    //             }
    //             return ;
    //         }
    //     }
    // }
    if (check)
    {
        const response = await Utils.APIRequest(`/api/games/sessions/${session_id}/state/players/${check.player_id}/`, 
            {move: check.move}, 
            "PATCH");
        if (!response.ok) {
            console.error("ERROR handleKeyDown");
        }
    }   
}

function getOppositeKeys(key)
{
    const inputs = getInputs();

    for (const player_id in inputs)
    {
        if (inputs[player_id].up.includes(key))
        {
            return {inputs: inputs[player_id].down, move:  'down'};
        }
        if (inputs[player_id].down.includes(key))
        {
            return {inputs: inputs[player_id].up, move: 'up'};
        }
    }
}

async function handleKeyUp(event)
{
    const key = event.key.toLowerCase();
    const check = checkInput(event);
    const opposite_keys = getOppositeKeys(key);

    keys_state[key] = false;
    if (opposite_keys)
    {
        for (const input of opposite_keys.inputs)
        {
            if (keys_state[input])
            {
                const response = await Utils.APIRequest(`/api/games/sessions/${session_id}/state/players/${check.player_id}/`, 
                    {move: opposite_keys.move}, 
                    "PATCH"); 
                if (!response.ok) {
                    console.error("ERROR handleKeyUp.");
                }
                return ;
            }
        }
    }
    if (check)
    {
        const response = await Utils.APIRequest(`/api/games/sessions/${session_id}/state/players/${check.player_id}/`, {move: null}, "PATCH"); 
        if (!response.ok) {
            console.error("ERROR handleKeyUp.");
        }
    }
}

async function initGame()
{
    try
	{
        await Utils.initWS('pong', ws_url, pongWSHandler);

        const response = await Utils.APIRequest(`/api/games/sessions/${session_id}/`);
        if (!response.ok) {
            console.error("Échec de récupération de la session de jeu.");
            return;
        }

        params = response.session.parameters;
        state = response.session.state;
        match = response.session.match;

        canvas.width = CANVAS_BASE_WIDTH;
        canvas.height = CANVAS_BASE_WIDTH / 2;

        const startResponse = await Utils.APIRequest(`/api/games/sessions/${session_id}/`, {}, "PUT");
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

function engine2D(state)
{
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const fieldWidth = canvas.width * CANVAS_WIDTH_RATIO;
    const fieldHeight = fieldWidth * params.field_ratio;
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
        radius: params.ball_radius * fieldWidth
    };

    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fillStyle = "white";
    ctx.fill();

    // Paddles
    ctx.font = "20px Arial";

    state.teams.forEach((team, index) => {
        ctx.fillStyle = colors[index];
        const scoreX = index === 0 ? canvas.width / 4 : (3 * canvas.width) / 4;
        ctx.fillText(team.score, scoreX, 30);

        team.players.forEach(player => {
            const paddle = {
                x: fieldX + player.coordinate_x * fieldWidth,
                y: fieldY + player.coordinate_y * fieldWidth,
                width: params.paddle_width * fieldWidth,
                height: team.paddle_length * fieldWidth
            };
            ctx.fillStyle = colors[index];
            ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);
        });
    });
}
