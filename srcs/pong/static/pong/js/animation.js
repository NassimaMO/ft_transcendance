import { threeJS } from './main.js'
import * as Geo from './buildGeometry.js'
let idx = 0

export function start()
{
	let animaID = requestAnimationFrame( start )
	threeJS.camera.rotation.x -= Math.PI / 128
	threeJS.camera.position.y = (Math.cos((Math.PI / 128) * idx) * 200 * -1)
	threeJS.camera.position.z = Math.sin((Math.PI / 128) * idx) * 200
	Geo.paddleLeft.object.position.z -= 3
	Geo.paddleLeft.rectLight.position.z -= 3
	Geo.paddleRight.object.position.z -= 3
	Geo.paddleRight.rectLight.position.z -= 3
	idx++
	if (idx == 64)
	{
		idx = 0
		cancelAnimationFrame(animaID)
	}
}
