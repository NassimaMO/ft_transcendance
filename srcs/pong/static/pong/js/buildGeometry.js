import * as THREE from 'three'
import * as Config from './config.js'

//export const puck = puck()
var textureLoader = new THREE.TextureLoader();
var lightMap = textureLoader.load('../../static/pong/media/images.png');
var wireMap = textureLoader.load('')
var backMap = textureLoader.load('../../static/pong/media/Background.png')
//var tableMap = textureLoader.load('')

export const puck = cylinder()
export const paddleLeft = paddle(Config.paddleLeftPosition, Config.paddleLeftSize)
export const paddleRight = paddle(Config.paddleRightPosition, Config.paddleRightSize)

function cylinder()
{
    const geometryCylinder = new THREE.CylinderGeometry( 5, 5, 3, 64 );
    const materialCylinder = new THREE.MeshStandardMaterial( { color: 0x00ff00, lightMap: lightMap, lightMapIntensity: 5} );
    const cylinder =
    {
        object: new THREE.Mesh( geometryCylinder, materialCylinder ),
        pointLight: new THREE.PointLight( 0x00ff00, 50, 0, 1),
    }
    cylinder.object.rotation.x = Math.PI / 2
    cylinder.pointLight.position.z = 1.5
    cylinder.pointLight.castShadow = true
    return cylinder;
}

function paddle(positionX, Size)
{
    const geometryPaddle = new THREE.BoxGeometry( Size[0], Size[1], Size[2] );
    const materialPaddle = new THREE.MeshStandardMaterial( { color: 0xff0000, lightMap: lightMap, lightMapIntensity: 3} );
    const paddle =
    {
        object: new THREE.Mesh( geometryPaddle, materialPaddle ),
        rectLight: new THREE.RectAreaLight( 0xff0000, 5, 10, 30),
		move: 0
    }
    paddle.object.position.set(positionX, 0, 192)
    paddle.rectLight.position.set(positionX, 0, 195)
    paddle.object.castShadow = true
    paddle.object.receiveShadow = true;
    return paddle
}

export function wallVertical(positionX, positionY, positionZ)
{
    const geometryWallVertical = new THREE.BoxGeometry( 5, 240, 5 );
    const materialWallVertical = new THREE.MeshStandardMaterial( { color: 0xff0000, lightMap: lightMap, lightMapIntensity: 5} );
    const wallVertical =
    {
        object: new THREE.Mesh( geometryWallVertical, materialWallVertical ),
        rectLight: new THREE.RectAreaLight( 0xff0000, 3, 5, 240),
        pointLight: new THREE.PointLight(0xff0000, 50, 0, 1)
    }
    wallVertical.object.position.set(positionX, positionY, positionZ)
    wallVertical.rectLight.position.set(positionX, positionY, positionZ)
    return wallVertical
}

export function wallHorizontal(positionX, positionY, positionZ)
{
    const geometryWallVertical = new THREE.BoxGeometry( 431, 5, 5 );
    const materialWallVertical = new THREE.MeshStandardMaterial( { color: 0xff0000, lightMap: lightMap, lightMapIntensity: 3} );
    const wallHorizontal =
    {
        object: new THREE.Mesh( geometryWallVertical, materialWallVertical ),
        rectLight: new THREE.RectAreaLight( 0xff0000, 3, 431, 5)
    }
    wallHorizontal.object.position.set(positionX, positionY, positionZ)
    wallHorizontal.rectLight.position.set(positionX, positionY, positionZ + 3)
    return wallHorizontal
}

function table()
{
	const geometryTable = new THREE.PlaneGeometry( 450, 240, 30, 10 );
	const materialTable = new THREE.MeshStandardMaterial( { color: 0xffffff, fog: false, wireframe: false} );
	const table = new THREE.Mesh( geometryTable, materialTable );
	table.receiveShadow = true;
    table.position.z = -4
	return table
}

export function map()
{
	const map =
	{
		wallLeft : wallVertical(-213, 0, 0),
		wallRight : wallVertical(213, 0, 0),
		wallUp : wallHorizontal(0, 120, 0),
		wallDown : wallHorizontal(0, -120, 0),
		table : table()
	}
	return (map)
}
