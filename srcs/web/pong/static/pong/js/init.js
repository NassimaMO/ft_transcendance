import * as THREE from 'three'
import * as Object from './buildGeometry.js'
import * as Config from './config.js'


export let windowWidth = window.innerWidth
export let windowHeight = window.innerHeight

export function setWindowHeight(innerHeight)
{
	windowWidth = innerHeight;
}

export function setWindowWidth(innerWidth)
{
	windowWidth = innerWidth;
}

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
	threeJs.renderer.setSize( window.innerWidth, window.innerHeight - 150)
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

function buildObject(threeJs, puck, paddle)
{
	threeJs.scene.add(paddle.Left.object, paddle.Left.rectLight,
				paddle.Right.object, paddle.Right.rectLight,
				puck.object, puck.pointLight);
	if (Config.mode == 2)
	{
		threeJs.scene.add(paddle.DoubleRight.object, paddle.DoubleRight.rectLight,
		paddle.DoubleLeft.object, paddle.DoubleLeft.rectLight);
	}
}

function buildLight(threeJs)
{

}

export function init(puck, paddle)
{
	const threeJs = initThreeJs()
	buildMap(threeJs)
	buildLight(threeJs)
	buildObject(threeJs, puck, paddle)
	return threeJs
}
