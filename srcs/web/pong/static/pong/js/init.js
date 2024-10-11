import * as THREE from 'three'
import * as Object from './buildObject.js'

function initThreeJs()
{
	const renderer = new THREE.WebGLRenderer({antialias: true})
	const threeJs =
	{
		scene : new THREE.Scene(),
		camera : new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 ),
		renderer
	}
	threeJs.renderer.setSize( window.innerWidth - 10, window.innerHeight - 200)
	threeJs.camera.position.z = 200;
	document.body.appendChild( renderer.domElement )
	return (threeJs)
}

function buildMap(threeJs)
{
	const	map	= Object.map()
	threeJs.scene.add(map.wallLeft.object, map.wallLeft.rectLight,
					map.wallRight.object, map.wallRight.rectLight,
					map.wallUp.object, map.wallUp.rectLight,
					map.wallDown.object, map.wallDown.rectLight,
					map.table
	)
}

function buildObject(threeJs, puck, paddleLeft, paddleRight)
{
	threeJs.scene.add(paddleLeft.object, paddleLeft.rectLight,
				paddleRight.object, paddleRight.rectLight,
				puck.object, puck.pointLight);
}

export function init(puck, paddleLeft, paddleRight)
{
	const threeJs = initThreeJs()
	buildMap(threeJs)
	buildObject(threeJs, puck, paddleLeft, paddleRight)
	return threeJs
}
