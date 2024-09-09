//import { OrbitControls } from 'orbitcontrols';
import * as Obj from './buildGeometry.js'
import * as Init from './init.js'
import * as Move from './move.js'
import * as Animation from './animation.js'
import * as Config from './config.js'

const keyCode = {};
//const controls = new OrbitControls(threeJS.camera, threeJS.renderer.domElement)
export const threeJS = Init.init(Obj.puck, Obj.paddleLeft, Obj.paddleRight)
document.addEventListener("keydown", keyPress);
document.addEventListener("keyup", keyRelease);

function game()
{
	requestAnimationFrame( game );
	Move.puckMovement(Obj.puck)
	Move.collision(Obj.puck, Obj.paddleRight, Obj.paddleLeft)
	Move.movePaddle(Obj.paddleLeft, Obj.paddleRight);
	if (Init.windowHeight != window.innerHeight || Init.windowWidth != window.innerWidth)
	{
		threeJS.renderer.setSize( window.innerWidth - 10, window.innerHeight - 200)
		threeJS.camera.position.z = 200;
		threeJS.camera.aspect = (window.innerWidth / window.innerHeight)
		threeJS.camera.updateProjectionMatrix();
		Init.windowHeight = window.innerHeight
		Init.windowWidth = window.innerWidth
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
        Obj.paddleRight.move = 1;
    else if (keyCode[40])
        Obj.paddleRight.move = -1;
    else
        Obj.paddleRight.move = 0;
    if (keyCode[87])
        Obj.paddleLeft.move = 1;
    else if (keyCode[83])
        Obj.paddleLeft.move = -1;
    else
        Obj.paddleLeft.move = 0;
}

threeJS.camera.rotation.x =  Math.PI / 2
threeJS.camera.position.y = -200

Animation.start()
game()
