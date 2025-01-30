import * as THREE from 'three'
import * as Config from './config.js'

var textureLoader = new THREE.TextureLoader();
var lightMap = textureLoader.load('../../static/pong/media/images.png');
var wireMap = textureLoader.load('')
var backMap = textureLoader.load('../../static/pong/media/Background.png')
//var tableMap = textureLoader.load('')

export const puck = cylinder()
export const paddle = 
{
	Left: buildPaddle(Config.paddleLeftPosition, Config.paddleLeftSize, Config.paddleLeftColor),
	Right: buildPaddle(Config.paddleRightPosition, Config.paddleRightSize, Config.paddleRightColor),
}
if (Config.mode == 2)
{
	paddle.DoubleLeft = buildPaddle(Config.paddleDoubleLeftPosition, Config.paddleDoubleLeftSize, Config.paddleDoubleLeftColor)
	paddle.DoubleRight = buildPaddle(Config.paddleDoubleRightPosition, Config.paddleDoubleRightSize, Config.paddleDoubleRightColor)
}

function cylinder()
{
    const geometryCylinder = new THREE.CylinderGeometry( 5, 5, 3, 64 );
    const materialCylinder = new THREE.MeshStandardMaterial( { color: Config.puckColor, lightMap: lightMap, lightMapIntensity: 5} );
    const cylinder =
    {
        object: new THREE.Mesh( geometryCylinder, materialCylinder ),
        pointLight: new THREE.PointLight( Config.puckColor, 50, 0, 1),
    }
    cylinder.object.rotation.x = Math.PI / 2
    cylinder.object.position.set(Config.puckPosition[0], Config.puckPosition[1], Config.puckPosition[2])
    cylinder.pointLight.position.set(Config.puckPosition[0], Config.puckPosition[1], Config.puckPosition[2] + 1.5)
    cylinder.pointLight.castShadow = true
    return cylinder;
}

function buildPaddle(position, Size, Color)
{
    const geometryPaddle = new THREE.BoxGeometry( Size[0], Size[1], Size[2] );
    const materialPaddle = new THREE.MeshStandardMaterial( { color: Color, lightMap: lightMap, lightMapIntensity: 3} );
    const paddle =
    {
        object: new THREE.Mesh( geometryPaddle, materialPaddle ),
        rectLight: new THREE.RectAreaLight( Color, Size[2], Size[0], Size[1]),
		move: 0
    }
    paddle.object.position.set(position[0], position[1], position[2])
    paddle.rectLight.position.set(position[0], position[1], position[2] + 5)
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
    const geometryWallVertical = new THREE.BoxGeometry( Config.tableWidth - 20, 5, 5 );
    const materialWallVertical = new THREE.MeshStandardMaterial( { color: 0xff0000, lightMap: lightMap, lightMapIntensity: 3} );
    const wallHorizontal =
    {
        object: new THREE.Mesh( geometryWallVertical, materialWallVertical ),
        rectLight: new THREE.RectAreaLight( 0xff0000, 3, Config.tableWidth - 20, 5)
    }
    wallHorizontal.object.position.set(positionX, positionY, positionZ)
    wallHorizontal.rectLight.position.set(positionX, positionY, positionZ + 3)
    return wallHorizontal
}

function table()
{
	const geometryTable = new THREE.PlaneGeometry( Config.tableWidth, Config.tableHeight, 30, 10 );
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
		wallUp : wallHorizontal(0, (Config.tableHeight / 2), 0),
		wallDown : wallHorizontal(0, -1 * (Config.tableHeight / 2), 0),
		table : table()
	}
	return (map)
}
