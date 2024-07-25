//import { OrbitControls } from 'orbitcontrols';
import {puck, paddleLeft, paddleRight} from './buildGeometry.js'
import {init, windowWidth, windowHeight} from './init.js'
import * as Move from './move.js'
import * as Animation from './animation .js'
import * as Config from './config.js'

let idx = 0

const keyCode = {};
export const threeJS = init(puck, paddleLeft, paddleRight)
//const controls = new OrbitControls(threeJS.camera, threeJS.renderer.domElement)
document.addEventListener("keydown", keyPress);
document.addEventListener("keyup", keyRelease);

function game() 
{
	requestAnimationFrame( game );
	Move.puckMovement(puck)
	Move.collision(puck, paddleRight, paddleLeft)
	Move.movePaddle(paddleLeft, paddleRight);
	if (windowHeight != window.innerHeight || windowWidth != window.innerWidth)
	{
		threeJS.renderer.setSize( window.innerWidth - 10, window.innerHeight - 200)
		threeJS.camera.position.z = 200;
		threeJS.camera.aspect = (window.innerWidth / window.innerHeight)
		threeJS.camera.updateProjectionMatrix();
		windowHeight = window.innerHeight
		windowWidth = window.innerWidth
	}
	threeJS.renderer.render( threeJS.scene, threeJS.camera );
}

function keyPress(event) 
{
    keyCode[event.which] = true;
    updatePaddleMovement();
}

function keyRelease(event) 
{
    keyCode[event.which] = false;
    updatePaddleMovement();
}

function updatePaddleMovement()
{
    if (keyCode[38])
        paddleRight.move = 1;
    else if (keyCode[40])
        paddleRight.move = -1;
    else
        paddleRight.move = 0;
    if (keyCode[87])
        paddleLeft.move = 1;
    else if (keyCode[83])
        paddleLeft.move = -1;
    else
        paddleLeft.move = 0;
}

threeJS.camera.rotation.x =  Math.PI / 2
threeJS.camera.position.y = -200

Animation.start()
game()
