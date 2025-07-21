/* ---------------------------------- */
/*               Mode                 */
/* ---------------------------------- */
 
export const mode = 2;

/* ---------------------------------- */
/*              Ground                */
/* ---------------------------------- */

export const groundHeight = 160;
export const groundWidth = 90;
export let cameraZ = groundHeight * 0.8;
if (groundWidth * 0.44 > cameraZ)
	cameraZ = groundWidth * 0.44

/* ---------------------------------- */
/*               Puck                 */
/* ---------------------------------- */

export const puckSpeed = 1.5
export const puckPosition = [0, 0, 190]
export const puckDiameter = 5
export const puckColor = 0xffffff
export let directionX = 1;
export function changeDirectionX() { directionX *= -1 }
export let directionY = 1;
export function changeDirectionY() { directionY *= -1 }

/* ---------------------------------- */
/*            	  Paddle              */
/* ---------------------------------- */

export const paddleSize = [5, 15, 5] // [Width, Length, Height]
export const paddleSpeed = 10
export const paddleColor = [0x0000ff, 0xff0000, 0x0000ff, 0x0000ff]; // [left, right, ndLeft ,ndRight]