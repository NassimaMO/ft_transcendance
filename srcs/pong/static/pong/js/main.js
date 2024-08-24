import * as THREE from 'three';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { OrbitControls } from 'three/addons/Addons.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import * as Object from './buildObject.js'
import * as Init from "./init.js"
import * as Move from './move.js'

let directionX = 1;
let directionY = 1;
let puckSpeed = 3
let windowWidth = window.innerWidth
let windowHeight = window.innerHeight
const keyCode = {};
const puck = Object.puck()
const paddleLeft = Object.paddle(-180, 0, 0)
const paddleRight = Object.paddle(180, 0, 0)
const threeJS = Init.init(puck, paddleLeft, paddleRight)
const controls = new OrbitControls(threeJS.camera, threeJS.renderer.domElement)
document.addEventListener("keydown", keyPress, false);
document.addEventListener("keyup", keyRelease, false);


function startGame() {
    // Open a WebSocket connection to the server
    const gameSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/game/create_game/'
    );

    // When the connection is open, send a message to create a game
    gameSocket.onopen = function() {
        const message = {
            type: 'create_game',
            player_one_id: 1,
            player_two_id: 2
        };
        gameSocket.send(JSON.stringify(message));
    };

    // Handle messages received from the server
    gameSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        if (data.type === 'game_created') {
            const gameSessionID = data.id;
            game(gameSocket, gameSessionID);
        }
    };

    // Handle any errors
    gameSocket.onerror = function(e) {
        console.error('WebSocket error:', e);
    };

    // Handle connection close
    gameSocket.onclose = function(e) {
        console.error('WebSocket connection closed:', e);
    };
}

function updateGameState(gameSocket) {
    // Send a request to the server to update the game state
    const message = {
        type: 'update_state'
    };
    gameSocket.send(JSON.stringify(message));
}

function game(gameSocket, gameSessionID) {
    requestAnimationFrame(function() { game(gameSocket, gameSessionID); });

    // Request game state update from the server
    updateGameState(gameSocket);

    // Handle window resizing
    if (windowHeight != window.innerHeight || windowWidth != window.innerWidth) {
        threeJS.renderer.setSize(window.innerWidth - 10, window.innerHeight - 200);
        threeJS.camera.position.z = 200;
        threeJS.camera.aspect = (window.innerWidth / window.innerHeight);
        threeJS.camera.updateProjectionMatrix();
        windowHeight == window.innerHeight;
        windowWidth == window.innerWidth;
    }

    // Render the scene
    threeJS.renderer.render(threeJS.scene, threeJS.camera);
}

function keyRelease(event) {
    keyCode[event.which] = false;
}

function keyPress(event, gameSocket) {
    keyCode[event.which] = true;

    if (keyCode[38]) {
        movePaddleServer(gameSocket, 'right', 'move_up');
    }
    if (keyCode[40]) {
        movePaddleServer(gameSocket, 'right', 'move_down');
    }
    if (keyCode[87]) {
        movePaddleServer(gameSocket, 'left', 'move_up');
    }
    if (keyCode[83]) {
        movePaddleServer(gameSocket, 'left', 'move_down');
    }
}

function movePaddleServer(gameSocket, paddle, action) {
    const message = {
        type: 'control',
        paddle: paddle,
        action: action
    };
    gameSocket.send(JSON.stringify(message));
}

// Start the game when the page loads
startGame();

/*function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.getAttribute('content') : null;
}

function startGame() {
    fetch('/api/games/create_game/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            player_one_id: 1,
            player_two_id: 2
        })
    })
    .then(response => response.json())
    .then(data => {
        const gameSessionID = data.id;
        game(gameSessionID);
    })
    .catch(error => console.error('Error:', error));
}

function updateGameState(gameSessionID) {
	fetch('/api/games/${gameSessionID}/update_state/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
	.then(response => response.json())
	.then(data => {
		puck.object.position.x = data.ball_position_x;
		puck.object.position.y = data.ball_position_y;
		puck.pointLight.position.x = data.ball_position_x;
		puck.pointLight.position.y = data.ball_position_y;
		paddleLeft.object.position.y = data.position_player_one;
		paddleRight.object.position.y = data.position_player_two;
	})
	.catch(error => console.error('Error:', error));
}

function game(gameSessionID) {
	requestAnimationFrame( game );
	updateGameState(gameSessionID);
	if (windowHeight != window.innerHeight || windowWidth != window.innerWidth)
	{
		threeJS.renderer.setSize( window.innerWidth - 10, window.innerHeight - 200)
		threeJS.camera.position.z = 200;
		threeJS.camera.aspect = (window.innerWidth / window.innerHeight)
		threeJS.camera.updateProjectionMatrix();
		windowHeight == window.innerHeight
		windowWidth == window.innerWidth
	}
	threeJS.renderer.render( threeJS.scene, threeJS.camera );
}

function keyRelease(event)
{
	keyCode[event.which] = false;
}

function keyPress(event, gameSessionID) {
    keyCode[event.which] = true;

    if (keyCode[38]) {
        movePaddleServer('right', 'move_up', gameSessionID);
    }
    if (keyCode[40]) {
        movePaddleServer('right', 'move_down', gameSessionID);
    }
    if (keyCode[87]) {
        movePaddleServer('left', 'move_up', gameSessionID);
    }
    if (keyCode[83]) {
        movePaddleServer('left', 'move_down', gameSessionID);
    }
}

function movePaddleServer(paddle, action, gameSessionID) {
    fetch('/api/games/${gameSessionID}/control/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ paddle: paddle, action: action })
    });
}


startGame()
*/