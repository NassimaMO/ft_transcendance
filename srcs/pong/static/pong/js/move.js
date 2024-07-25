import * as Config from './config.js'

let idx = 0

export function movePaddle(paddleLeft, paddleRight)
{
	if ((paddleLeft.object.position.y <= 96 && paddleLeft.move == 1) || (paddleLeft.object.position.y >= -96 && paddleLeft.move == -1))
	{
		paddleLeft.object.position.y += paddleLeft.move * Config.paddleLeftSpeed
		paddleLeft.rectLight.position.y += paddleLeft.move * Config.paddleLeftSpeed
	}
	if ((paddleRight.object.position.y <= 96 && paddleRight.move == 1) || (paddleRight.object.position.y >= -96 && paddleRight.move == -1))
	{
		paddleRight.object.position.y += paddleRight.move * Config.paddleRightSpeed
		paddleRight.rectLight.position.y += paddleRight.move * Config.paddleRightSpeed
	}
}

export function puckMovement(puck)
{
	puck.object.rotation.y += Config.puckSpeed * Config.directionY
	puck.object.position.x += Config.puckSpeed * Config.directionX;
	puck.object.position.y += Config.puckSpeed * Config.directionY;
	puck.pointLight.position.x += Config.puckSpeed * Config.directionX;
	puck.pointLight.position.y += Config.puckSpeed * Config.directionY;
}

export function collision(puck, paddleRight, paddleLeft)
{
	if (puck.object.position.x + 3 >= paddleRight.object.position.x - 5 && puck.object.position.x + 3 <= paddleRight.object.position.x && puck.object.position.y <= paddleRight.object.position.y + 15 && puck.object.position.y >= paddleRight.object.position.y - 15)
	{
		Config.changeDirectionX()
		puck.object.position.x = paddleRight.object.position.x - 8
		puck.pointLight.position.x = paddleRight.object.position.x - 8
	}
	if (puck.object.position.x - 3 <= paddleLeft.object.position.x + 5 && puck.object.position.x - 3 <= paddleLeft.object.position.x && puck.object.position.y <= paddleLeft.object.position.y + 15 && puck.object.position.y >= paddleLeft.object.position.y - 15)
	{
		Config.changeDirectionX()
		puck.object.position.x = paddleLeft.object.position.x + 8
		puck.pointLight.position.x = paddleLeft.object.position.x + 8
	}
	if (puck.object.position.y + 3 >= 120 - 5)
		Config.changeDirectionY()
	if (puck.object.position.y - 3 <= -120 + 5)
		Config.changeDirectionY()
	if (puck.object.position.x >= 203 || puck.object.position.x <= -203)
	{
		puck.object.position.x = 0
		puck.pointLight.position.x = 0
		puck.object.position.y = 0
		puck.pointLight.position.y = 0
	}
}