import * as Config from './config.js'

let idx = 0

export function movePaddle(paddleLeft, paddleRight, paddleDoubleLeft, paddleDoubleRight)
{
	if ((paddleLeft.object.position.y <= (Config.tableHeight / 2 ) - 30 && paddleLeft.move == 1) || (paddleLeft.object.position.y >= -1 * (Config.tableHeight / 2 ) + 30 && paddleLeft.move == -1))
	{
		paddleLeft.object.position.y += paddleLeft.move * Config.paddleLeftSpeed
		paddleLeft.rectLight.position.y += paddleLeft.move * Config.paddleLeftSpeed
	}
	if ((paddleRight.object.position.y <= (Config.tableHeight / 2 ) - 30 && paddleRight.move == 1) || (paddleRight.object.position.y >= -1 * (Config.tableHeight / 2 ) + 30 && paddleRight.move == -1))
	{
		paddleRight.object.position.y += paddleRight.move * Config.paddleRightSpeed
		paddleRight.rectLight.position.y += paddleRight.move * Config.paddleRightSpeed
	}
	if ((paddleDoubleLeft.object.position.y <= (Config.tableHeight / 2 ) - 30 && paddleDoubleLeft.move == 1) || (paddleDoubleLeft.object.position.y >= -1 * (Config.tableHeight / 2 ) + 30 && paddleDoubleLeft.move == -1))
	{
		paddleDoubleLeft.object.position.y += paddleDoubleLeft.move * Config.paddleDoubleLeftSpeed
		paddleDoubleLeft.rectLight.position.y += paddleDoubleLeft.move * Config.paddleDoubleLeftSpeed
	}
	if ((paddleDoubleRight.object.position.y <= (Config.tableHeight / 2 ) - 30 && paddleDoubleRight.move == 1) || (paddleDoubleRight.object.position.y >= -1 * (Config.tableHeight / 2 ) + 30 && paddleDoubleRight.move == -1))
	{
		paddleDoubleRight.object.position.y += paddleDoubleRight.move * Config.paddleDoubleRightSpeed
		paddleDoubleRight.rectLight.position.y += paddleDoubleRight.move * Config.paddleDoubleRightSpeed
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
	if (puck.object.position.x + (Config.puckSize[0] / 2) >= paddleRight.object.position.x - (Config.paddleRightSize[0] / 2) && puck.object.position.x + (Config.puckSize[0] / 2) <= paddleRight.object.position.x && puck.object.position.y <= paddleRight.object.position.y + (Config.paddleRightSize[1] / 2) && puck.object.position.y >= paddleRight.object.position.y - (Config.paddleRightSize[1] / 2))
	{
		Config.changeDirectionX()
		puck.object.position.x = paddleRight.object.position.x - Config.paddleRightSize[0]
		puck.pointLight.position.x = paddleRight.object.position.x - Config.paddleRightSize[0]
	}
	if (puck.object.position.x - (Config.puckSize[0] / 2) <= paddleLeft.object.position.x + (Config.paddleRightSize[0] / 2) && puck.object.position.x - (Config.puckSize[0] / 2) >= paddleLeft.object.position.x && puck.object.position.y <= paddleLeft.object.position.y + (Config.paddleLeftSize[1] / 2) && puck.object.position.y >= paddleLeft.object.position.y - (Config.paddleLeftSize[1] / 2) )
	{
		Config.changeDirectionX()
		puck.object.position.x = paddleLeft.object.position.x + Config.paddleLeftSize[0]
		puck.pointLight.position.x = paddleLeft.object.position.x + Config.paddleLeftSize[0]
	}
	if (puck.object.position.y + Config.puckSize[0] >= (Config.tableHeight / 2 ) - 5)
		Config.changeDirectionY()
	if (puck.object.position.y - Config.puckSize[0] <= -1 * (Config.tableHeight / 2 ) + 5)
		Config.changeDirectionY()
	if (puck.object.position.x - Config.puckSize[0] >= (Config.tableWidth / 2) || puck.object.position.x + Config.puckSize[0] <= -1 * (Config.tableWidth / 2))
	{
		puck.object.position.x = 0
		puck.pointLight.position.x = 0
		puck.object.position.y = 0
		puck.pointLight.position.y = 0
	}
}
