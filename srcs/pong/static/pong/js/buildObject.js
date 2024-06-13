import * as THREE from 'three';

var textureLoader = new THREE.TextureLoader();
var lightMap = textureLoader.load('/static/pong/media/texture.jpg');

export function puck()
{
    const geometryCylinder = new THREE.CylinderGeometry( 5, 5, 3, 64 );
    const materialCylinder = new THREE.MeshStandardMaterial( { color: 0x00ff00, lightMap: lightMap, lightMapIntensity: 5} );
    let puck =
    {
        object: new THREE.Mesh( geometryCylinder, materialCylinder ),
        pointLight: new THREE.PointLight( 0x00ff00, 30)
    }
    puck.object.rotation.x = Math.PI / 2
    return puck;
}

export function paddle(positionX, positionY, positionZ)
{
    const geometryPaddle = new THREE.BoxGeometry( 10, 30, 5 );
    const materialPaddle = new THREE.MeshStandardMaterial( { color: 0xff0000, lightMap: lightMap, lightMapIntensity: 5} );
    let paddle =
    {
        object: new THREE.Mesh( geometryPaddle, materialPaddle ),
        rectLight: new THREE.RectAreaLight( 0xff0000, 3, 10, 30)
    }
    paddle.object.position.set(positionX, positionY, positionZ)
    paddle.rectLight.position.set(positionX, positionY, positionZ)
    return paddle
}

export function wallVertical(positionX, positionY, positionZ)
{
    const geometryWallVertical = new THREE.BoxGeometry( 5, 240, 5 );
    const materialWallVertical = new THREE.MeshStandardMaterial( { color: 0xff0000, lightMap: lightMap, lightMapIntensity: 5} );
    let wallVertical =
    {
        object: new THREE.Mesh( geometryWallVertical, materialWallVertical ),
        rectLight: new THREE.RectAreaLight( 0xff0000, 3, 5, 240)
    }
    wallVertical.object.position.set(positionX, positionY, positionZ)
    wallVertical.rectLight.position.set(positionX, positionY, positionZ)
    return wallVertical
}

export function wallHorizontal(positionX, positionY, positionZ)
{
    const geometryWallVertical = new THREE.BoxGeometry( 427, 5, 5 );
    const materialWallVertical = new THREE.MeshStandardMaterial( { color: 0xff0000, lightMap: lightMap, lightMapIntensity: 5} );
    let wallHorizontal =
    {
        object: new THREE.Mesh( geometryWallVertical, materialWallVertical ),
        rectLight: new THREE.RectAreaLight( 0xff0000, 3, 427, 5)
    }
    wallHorizontal.object.position.set(positionX, positionY, positionZ)
    wallHorizontal.rectLight.position.set(positionX, positionY, positionZ)
    return wallHorizontal
}