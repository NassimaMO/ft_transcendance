console.log("0")
import * as Obj from './buildGeometry.js'
import * as Init from './init.js'
import * as Move from './move.js'
import * as Animation from './animation.js'
import * as Config from './config.js'
import { end } from './animation.js'

const keyCode = {};
export const threeJS = Init.init(Obj.puck, Obj.paddle)
document.addEventListener("keydown", keyPress);
document.addEventListener("keyup", keyRelease);

function game()
{
    requestAnimationFrame( game );
	console.log(end)
	if (end == 1)
	{
		Move.puckMovement(Obj.puck)
		Move.collision(Obj.puck, Obj.paddle)
    	Move.movePaddle(Obj.paddle);
		if (Init.windowHeight != window.innerHeight || Init.windowWidth != window.innerWidth)
		{
			threeJS.renderer.setSize( window.innerWidth - 10, window.innerHeight - 150)
			threeJS.camera.position.z = Config.cameraZ;
        	threeJS.camera.aspect = (window.innerWidth / window.innerHeight)
        	threeJS.camera.updateProjectionMatrix();
        	Init.setWindowHeight(window.innerHeight);
        	Init.setWindowWidth(window.innerWidth);
		}
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
        Obj.paddle.Right.move = 1;
    else if (keyCode[40])
        Obj.paddle.Right.move = -1;
    else
        Obj.paddle.Right.move = 0;
    if (keyCode[87])
        Obj.paddle.Left.move = 1;
    else if (keyCode[83])
        Obj.paddle.Left.move = -1;
    else
        Obj.paddle.Left.move = 0;
    if (Config.mode == 2)
    {
        if (keyCode[79])
            Obj.paddle.DoubleRight.move = 1;
        else if (keyCode[75])
            Obj.paddle.DoubleRight.move = -1;
        else
            Obj.paddle.DoubleRight.move = 0;
        if (keyCode[69])
            Obj.paddle.DoubleLeft.move = 1;
        else if (keyCode[68])
            Obj.paddle.DoubleLeft.move = -1;
        else
            Obj.paddle.DoubleLeft.move = 0;
    }
}

threeJS.camera.rotation.x =  Math.PI / 2
threeJS.camera.position.y = -1 * Config.cameraZ

Animation.start()
game()
