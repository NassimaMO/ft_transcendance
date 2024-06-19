import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/Addons.js';
import * as Object from './buildObject.js'
import * as Init from './init.js'

const puck = Object.puck()
const paddleLeft = Object.paddle(-180, 0, 0)
const paddleRight = Object.paddle(180, 0, 0)
const threeJS = Init.init(puck, paddleLeft, paddleRight)
const controls = new OrbitControls(threeJS.camera, threeJS.renderer.domElement)
let directionX = 1;
let directionY = 1;

function colision()
{
	if (puck.object.position.x + 2.5 >= paddleRight.object.position.x - 5 && puck.object.position.y <= paddleRight.object.position.y + 15 && puck.object.position.y >= paddleRight.object.position.y - 15)
		directionX *= -1
	if (puck.object.position.x - 2.5 <= paddleLeft.object.position.x + 5)
		directionX *= -1
	if (puck.object.position.y + 2.5 >= 120)
		directionY *= -1;
	if (puck.object.position.y - 2.5 <= -120)
		directionY *= -1;
	if (puck.object.position.x >= 203)
	{
		puck.object.position.x = 0
		puck.pointLight.position.x = 0
	}
}

function puckMouvement()
{
	puck.object.rotation.y += 2 * directionY
	puck.object.position.x += 2 * directionX;
	puck.object.position.y += 2 * directionY;
	puck.pointLight.position.x += 2 *directionX;
	puck.pointLight.position.y += 2 *directionY;
}

function game() {
	requestAnimationFrame( game );
	puckMouvement()
	colision()
	threeJS.renderer.render( threeJS.scene, threeJS.camera );
}

document.addEventListener("keydown", onDocumentKeyDown, false);
function onDocumentKeyDown(event)
{
	var keyCode = event.which;
	if (keyCode === 38 && paddleRight.object.position.y < 95)
	{
		paddleRight.object.position.y += 2
		paddleRight.rectLight.position.y += 2
	}
	else if (event.keyCode === 40 && paddleRight.object.position.y > -95)
	{
		paddleRight.object.position.y -= 2
		paddleRight.rectLight.position.y -= 2
	}
}

game()
