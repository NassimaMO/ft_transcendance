import * as THREE from 'three'
import * as Object from './buildGeometry.js'


export let windowWidth = window.innerWidth
export let windowHeight = window.innerHeight

function initThreeJs()
{
	const renderer = new THREE.WebGLRenderer({antialias: true})
	const threeJs =
	{
		scene : new THREE.Scene(),
		camera : new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 ),
		renderer
	}
	threeJs.renderer.shadowMap.enabled = true
	threeJs.renderer.setSize( window.innerWidth, window.innerHeight - 200)
	document.body.appendChild( renderer.domElement )
	return (threeJs)
}

function buildMap(threeJs)
{
	const	map	= Object.map()
	threeJs.scene.add(
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

function buildLight(threeJs)
{

}

export function init(puck, paddleLeft, paddleRight)
{
	const threeJs = initThreeJs()
	buildMap(threeJs)
	buildLight(threeJs)
	buildObject(threeJs, puck, paddleLeft, paddleRight)
	return threeJs
}
