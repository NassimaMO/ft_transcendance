/* ---------------------------------- */
/*               Table                */
/* ---------------------------------- */

export let tableHeight = 250;
export let tableWidth = 450;

/* ---------------------------------- */
/*               Puck                 */
/* ---------------------------------- */

export let puckSpeed = 1.5
export let puckSize = [5, 5, 3]
export let directionX = 1;
export function changeDirectionX() { directionX *= -1 }
export let directionY = 1;
export function changeDirectionY() { directionY *= -1 }

/* ---------------------------------- */
/*            PaddleRight             */
/* ---------------------------------- */

export let paddleRightPosition = 3 * (tableWidth / 8)
export let paddleRightSize = [10, 30, 5] // [Width, Length, Height]
export let paddleRightSpeed = 10


/* ---------------------------------- */
/*            PaddleLeft              */
/* ---------------------------------- */

export let paddleLeftPosition = -3 * (tableWidth / 8)
export let paddleLeftSize = [10, 30, 5] // [Width, Length, Height]
export let paddleLeftSpeed = 10


