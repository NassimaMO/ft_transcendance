/* ---------------------------------- */
/*               Mode                 */
/* ---------------------------------- */
 
export const mode = 2;

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
export const puckPosition = [0, 0, 190]
export const puckSize = [5, 5, 3]
export const puckColor = 0xffffff
export let directionX = 1;
export function changeDirectionX() { directionX *= -1 }
export let directionY = 1;
export function changeDirectionY() { directionY *= -1 }

/* ---------------------------------- */
/*            PaddleRight             */
/* ---------------------------------- */

export const paddleRightPosition = [3 * (tableWidth / 8), tableHeight / 4, 192]
export const paddleRightSize = [10, 30, 5] // [Width, Length, Height]
export const paddleRightSpeed = 10
export const paddleRightColor = 0x0000ff;


/* ---------------------------------- */
/*            PaddleLeft              */
/* ---------------------------------- */

export const paddleLeftPosition = [-3 * (tableWidth / 8), tableHeight / 4, 192]
export const paddleLeftSize = [10, 30, 5] // [Width, Length, Height]
export const paddleLeftSpeed = 10
export const paddleLeftColor = 0xff0000;


/* ---------------------------------- */
/*         PaddleDoubleRight          */
/* ---------------------------------- */

export const paddleDoubleRightPosition = [3 * (tableWidth / 8), -1 * (tableHeight / 4), 192]
export const paddleDoubleRightSize = [10, 30, 5] // [Width, Length, Height]
export const paddleDoubleRightSpeed = 10
export const paddleDoubleRightColor = 0x00ffff

/* ---------------------------------- */
/*         PaddleDoubleLeft           */
/* ---------------------------------- */

export const paddleDoubleLeftPosition = [-3 * (tableWidth / 8), -1 * (tableHeight / 4), 192]
export const paddleDoubleLeftSize = [10, 30, 5] // [Width, Length, Height]
export const paddleDoubleLeftSpeed = 10
export const paddleDoubleLeftColor = 0x00ffff