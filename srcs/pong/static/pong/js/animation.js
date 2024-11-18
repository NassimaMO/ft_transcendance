import { threeJS } from './main.js'
import * as Geo from './buildGeometry.js'
import * as Config from './config.js'

let idx = 0

export function start()
{
	let animaID = requestAnimationFrame( start )
	threeJS.camera.rotation.x -= Math.PI / 128
	threeJS.camera.position.y = (Math.cos((Math.PI / 128) * idx) * Config.cameraZ * -1)
	threeJS.camera.position.z = Math.sin((Math.PI / 128) * idx) * Config.cameraZ
	Geo.paddleLeft.object.position.z -= 3
	Geo.paddleLeft.rectLight.position.z -= 3
	Geo.paddleRight.object.position.z -= 3
	Geo.paddleRight.rectLight.position.z -= 3
	Geo.paddleDoubleLeft.object.position.z -= 3
	Geo.paddleDoubleLeft.rectLight.position.z -= 3
	Geo.paddleDoubleRight.object.position.z -= 3
	Geo.paddleDoubleRight.rectLight.position.z -= 3
	idx++
	if (idx == 64)
	{
		idx = 0
		cancelAnimationFrame(animaID)
	}
}
