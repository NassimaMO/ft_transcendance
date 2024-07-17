let	paddleSpeed = 5

export function movePaddle(side, direction, paddleLeft, paddleRight)
{
	if (side == "left")
	{
		paddleLeft.object.translateY(paddleSpeed * direction)
		paddleLeft.rectLight.translateY(paddleSpeed * direction)
	}
	else if (side == "right")
	{
		paddleRight.object.translateY(paddleSpeed * direction)
		paddleRight.rectLight.translateY(paddleSpeed * direction)
	}
}
