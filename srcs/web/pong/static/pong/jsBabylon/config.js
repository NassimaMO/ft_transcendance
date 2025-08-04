/* ---------------------------------- */
/*               Mode                 */
/* ---------------------------------- */
 
export const mode = 2;

/* ---------------------------------- */
/*              Ground                */
/* ---------------------------------- */

export const groundLength = 160;
export const groundHeight = 70;

/* ---------------------------------- */
/*               Puck                 */
/* ---------------------------------- */

export const puckSpeed = 1
export const puckPosition = [0, 0, 190]
export const puckDiameter = 4.5
export const puckColor = 0xffffff
export let directionX = 1;
export function changeDirectionX() { directionX *= -1 }
export let directionY = 1;
export function changeDirectionY() { directionY *= -1 }

/* ---------------------------------- */
/*            	  Paddle              */
/* ---------------------------------- */

export const paddleSize = [4, 15, 4] // [Width, Length, Height]
export const paddleSpeed = 3
export const paddleColor = ["#0000FF", "#FF0000", "#0000FF", "#0000FF"]; // [left, right, ndLeft ,ndRight]