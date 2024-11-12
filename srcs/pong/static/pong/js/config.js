/* ---------------------------------- */
/*               Table                */
/* ---------------------------------- */

export const tableHeight = 250;
export const tableWidth = 400;
export let cameraZ = tableHeight * 0.8;
if (tableWidth * 0.44 > cameraZ)
	cameraZ = tableWidth * 0.44

/* ---------------------------------- */
/*               Puck                 */
/* ---------------------------------- */

export const puckSpeed = 1.5
export const puckSize = [5, 5, 3]
export let directionX = 1;
export function changeDirectionX() { directionX *= -1 }
export let directionY = 1;
export function changeDirectionY() { directionY *= -1 }

/* ---------------------------------- */
/*            PaddleRight             */
/* ---------------------------------- */

export let paddleRightPosition = 3 * (tableWidth / 8)
export const paddleRightSize = [10, 30, 5] // [Width, Length, Height]
export const paddleRightSpeed = 10


/* ---------------------------------- */
/*            PaddleLeft              */
/* ---------------------------------- */

export let paddleLeftPosition = -3 * (tableWidth / 8)
export const paddleLeftSize = [10, 30, 5] // [Width, Length, Height]
export const paddleLeftSpeed = 10


