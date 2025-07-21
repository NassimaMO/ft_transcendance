import { threeJS } from './main.js'
import * as Geo from './buildGeometry.js'
import * as Config from './config.js'

var idx = 0
export var end = 0
let number = Math.floor(Math.random() * 10)
if (number % 2 == 0)
	Config.changeDirectionX()
number = number / 64

export function start()
{
	end = 0
	let animaID0 = requestAnimationFrame( start )

	threeJS.camera.rotation.x -= Math.PI / 128
	threeJS.camera.position.y = (Math.cos((Math.PI / 128) * idx) * Config.cameraZ * -1)
	threeJS.camera.position.z = Math.sin((Math.PI / 128) * idx) * Config.cameraZ
	Geo.paddle.Left.object.position.z -= 3
	Geo.paddle.Left.rectLight.position.z -= 3
	Geo.paddle.Right.object.position.z -= 3
	Geo.paddle.Right.rectLight.position.z -= 3
	if (Config.mode == 2)
	{
		Geo.paddle.DoubleLeft.object.position.z -= 3
		Geo.paddle.DoubleLeft.rectLight.position.z -= 3
		Geo.paddle.DoubleRight.object.position.z -= 3
		Geo.paddle.DoubleRight.rectLight.position.z -= 3
	}
	threeJS.renderer.render( threeJS.scene, threeJS.camera );
	idx++
	if (idx == 64)
	{
		idx = 0
		cancelAnimationFrame(animaID0)
		Geo.puck.object.material.color.setHex( Config.paddleRightColor )
		Geo.puck.pointLight.color.setHex(Config.paddleRightColor)
		flipCoin()
	}
}

export function flipCoin()
{
	let animaID1 = requestAnimationFrame( flipCoin )

	Geo.puck.object.position.z -= 3
	Geo.puck.pointLight.position.z -= 3
	Geo.puck.object.rotation.z += number * 3.14
	if (Math.floor(number * idx) % 2 == 0)
	{
		Geo.puck.object.material.color.setHex( Config.paddleLeftColor )
		Geo.puck.pointLight.color.setHex(Config.paddleLeftColor)
	}
	else
	{
		Geo.puck.object.material.color.setHex( Config.paddleRightColor )
		Geo.puck.pointLight.color.setHex(Config.paddleRightColor)
	}
	idx++
	if (idx == 64)
	{
		idx = 0
		end = 1
		Geo.puck.object.material.color.setHex( Config.puckColor )
		Geo.puck.pointLight.color.setHex(Config.puckColor)
		Geo.puck.object.rotation.z == 0
		Geo.puck.pointLight.rotation.z == 0
		cancelAnimationFrame(animaID1)
	}
}