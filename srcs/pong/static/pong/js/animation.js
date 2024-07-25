let idx = 0
import { threeJS } from './main'
import {puck, paddleLeft, paddleRight} from './buildGeometry.js'

export function start()
{
	let animaID = requestAnimationFrame( start )
	threeJS.camera.rotation.x -= Math.PI / 128
	threeJS.camera.position.y = (Math.cos((Math.PI / 128) * idx) * 200 * -1)
	threeJS.camera.position.z = Math.sin((Math.PI / 128) * idx) * 200
	paddleLeft.object.position.z -= 3
	paddleLeft.rectLight.position.z -= 3
	paddleRight.object.position.z -= 3
	paddleRight.rectLight.position.z -= 3
	idx++
	if (idx == 64)
	{
		idx = 0
		cancelAnimationFrame(animaID)
	}
}