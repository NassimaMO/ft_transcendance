import * as Config from './config.js'

let idx = 0

export function movePaddle(paddle)
{
	if ((paddle.Left.object.position.y <= (Config.tableHeight / 2 ) - 30 && paddle.Left.move == 1) || (paddle.Left.object.position.y >= -1 * (Config.tableHeight / 2 ) + 30 && paddle.Left.move == -1 && (Config.mode == 1 || (paddle.Left.object.position.y - 15 > paddle.DoubleLeft.object.position.y + 15))))
	{
		paddle.Left.object.position.y += paddle.Left.move * Config.paddleLeftSpeed
		paddle.Left.rectLight.position.y += paddle.Left.move * Config.paddleLeftSpeed
	}
	if ((paddle.Right.object.position.y <= (Config.tableHeight / 2 ) - 30 && paddle.Right.move == 1) || (paddle.Right.object.position.y >= -1 * (Config.tableHeight / 2 ) + 30 && paddle.Right.move == -1 && (Config.mode == 1 || (paddle.Right.object.position.y - 15 > paddle.DoubleRight.object.position.y + 15))))
	{
		paddle.Right.object.position.y += paddle.Right.move * Config.paddleRightSpeed
		paddle.Right.rectLight.position.y += paddle.Right.move * Config.paddleRightSpeed
	}
	if (Config.mode == 2)
	{
		if ((paddle.DoubleLeft.object.position.y <= (Config.tableHeight / 2 ) - 30 && paddle.DoubleLeft.move == 1 && (paddle.DoubleLeft.object.position.y + 15 < paddle.Left.object.position.y - 15)) || (paddle.DoubleLeft.object.position.y >= -1 * (Config.tableHeight / 2 ) + 30 && paddle.DoubleLeft.move == -1))
		{
			paddle.DoubleLeft.object.position.y += paddle.DoubleLeft.move * Config.paddleDoubleLeftSpeed
			paddle.DoubleLeft.rectLight.position.y += paddle.DoubleLeft.move * Config.paddleDoubleLeftSpeed
		}
		if ((paddle.DoubleRight.object.position.y <= (Config.tableHeight / 2 ) - 30 && paddle.DoubleRight.move == 1 && (paddle.DoubleRight.object.position.y + 15 < paddle.Right.object.position.y - 15)) || (paddle.DoubleRight.object.position.y >= -1 * (Config.tableHeight / 2 ) + 30 && paddle.DoubleRight.move == -1))
		{
			paddle.DoubleRight.object.position.y += paddle.DoubleRight.move * Config.paddleDoubleRightSpeed
			paddle.DoubleRight.rectLight.position.y += paddle.DoubleRight.move * Config.paddleDoubleRightSpeed
		}
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

export function collision(puck, paddle)
{
	if (puck.object.position.x + (Config.puckSize[0] / 2) >= paddle.Right.object.position.x - (Config.paddleRightSize[0] / 2) && puck.object.position.x + (Config.puckSize[0] / 2) <= paddle.Right.object.position.x && puck.object.position.y <= paddle.Right.object.position.y + (Config.paddleRightSize[1] / 2) && puck.object.position.y >= paddle.Right.object.position.y - (Config.paddleRightSize[1] / 2))
	{
		Config.changeDirectionX()
		puck.object.position.x = paddle.Right.object.position.x - Config.paddleRightSize[0]
		puck.pointLight.position.x = paddle.Right.object.position.x - Config.paddleRightSize[0]
	}
	if (puck.object.position.x - (Config.puckSize[0] / 2) <= paddle.Left.object.position.x + (Config.paddleRightSize[0] / 2) && puck.object.position.x - (Config.puckSize[0] / 2) >= paddle.Left.object.position.x && puck.object.position.y <= paddle.Left.object.position.y + (Config.paddleLeftSize[1] / 2) && puck.object.position.y >= paddle.Left.object.position.y - (Config.paddleLeftSize[1] / 2) )
	{
		Config.changeDirectionX()
		puck.object.position.x = paddle.Left.object.position.x + Config.paddleLeftSize[0]
		puck.pointLight.position.x = paddle.Left.object.position.x + Config.paddleLeftSize[0]
	}
	if (Config.mode == 2)
	{
		if (puck.object.position.x + (Config.puckSize[0] / 2) >= paddle.DoubleRight.object.position.x - (Config.paddleDoubleRightSize[0] / 2) && puck.object.position.x + (Config.puckSize[0] / 2) <= paddle.DoubleRight.object.position.x && puck.object.position.y <= paddle.DoubleRight.object.position.y + (Config.paddleDoubleRightSize[1] / 2) && puck.object.position.y >= paddle.DoubleRight.object.position.y - (Config.paddleDoubleRightSize[1] / 2))
		{
			Config.changeDirectionX()
			puck.object.position.x = paddle.DoubleRight.object.position.x - Config.paddleDoubleRightSize[0]
			puck.pointLight.position.x = paddle.DoubleRight.object.position.x - Config.paddleDoubleRightSize[0]
		}
		if (puck.object.position.x - (Config.puckSize[0] / 2) <= paddle.DoubleLeft.object.position.x + (Config.paddleDoubleRightSize[0] / 2) && puck.object.position.x - (Config.puckSize[0] / 2) >= paddle.DoubleLeft.object.position.x && puck.object.position.y <= paddle.DoubleLeft.object.position.y + (Config.paddleDoubleLeftSize[1] / 2) && puck.object.position.y >= paddle.DoubleLeft.object.position.y - (Config.paddleDoubleLeftSize[1] / 2) )
		{
			Config.changeDirectionX()
			puck.object.position.x = paddle.DoubleLeft.object.position.x + Config.paddleDoubleLeftSize[0]
			puck.pointLight.position.x = paddle.DoubleLeft.object.position.x + Config.paddleDoubleLeftSize[0]
		}
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
