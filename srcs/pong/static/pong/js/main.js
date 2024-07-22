import * as THREE from 'three';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { OrbitControls } from 'three/addons/Addons.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import * as Object from './buildObject.js'
import * as Init from "./init.js"
import * as Move from './move.js'

let directionX = 1;
let directionY = 1;
let puckSpeed = 3
let windowWidth = window.innerWidth
let windowHeight = window.innerHeight
const keyCode = {};
const puck = Object.puck()
const paddleLeft = Object.paddle(-180, 0, 0)
const paddleRight = Object.paddle(180, 0, 0)
const threeJS = Init.init(puck, paddleLeft, paddleRight)
const controls = new OrbitControls(threeJS.camera, threeJS.renderer.domElement)
document.addEventListener("keydown", keyPress, false);
document.addEventListener("keyup", keyRelease, false);

/*
const loader = new FontLoader();
loader.load('https://threejs.org/examples/fonts/helvetiker_regular.typeface.json', function (font) {
	const color = 0x006699;

					const matDark = new THREE.LineBasicMaterial( {
						color: color,
						side: THREE.DoubleSide
					} );

					const matLite = new THREE.MeshBasicMaterial( {
						color: color,
						transparent: true,
						opacity: 0.4,
						side: THREE.DoubleSide
					} );

					const message = '   Three.js\nSimple text.';

					const shapes = font.generateShapes( message, 100 );

					const geometry = new THREE.ShapeGeometry( shapes );

					geometry.computeBoundingBox();

					const xMid = - 0.5 * ( geometry.boundingBox.max.x - geometry.boundingBox.min.x );

					geometry.translate( xMid, 0, 0 );

					// make shape ( N.B. edge view not visible )

					const text = new THREE.Mesh( geometry, matLite );
					text.position.z = - 150;
					scene.add( text );

					// make line shape ( N.B. edge view remains visible )

					const holeShapes = [];

					for ( let i = 0; i < shapes.length; i ++ ) {

						const shape = shapes[ i ];

						if ( shape.holes && shape.holes.length > 0 ) {

							for ( let j = 0; j < shape.holes.length; j ++ ) {

								const hole = shape.holes[ j ];
								holeShapes.push( hole );

							}

						}

					}

					shapes.push.apply( shapes, holeShapes );

					const lineText = new THREE.Object3D();

					for ( let i = 0; i < shapes.length; i ++ ) {

						const shape = shapes[ i ];

						const points = shape.getPoints();
						const geometry = new THREE.BufferGeometry().setFromPoints( points );

						geometry.translate( xMid, 0, 0 );

						const lineMesh = new THREE.Line( geometry, matDark );
						lineText.add( lineMesh );

					}

					scene.add( lineText );

					render();
});*/

function colision()
{
	if (puck.object.position.x + 3 >= paddleRight.object.position.x - 5 && puck.object.position.x + 3 <= paddleRight.object.position.x && puck.object.position.y <= paddleRight.object.position.y + 15 && puck.object.position.y >= paddleRight.object.position.y - 15)
	{
		directionX *= -1
		puck.object.position.x = paddleRight.object.position.x - 8
		puck.pointLight.position.x = paddleRight.object.position.x - 8
	}
	if (puck.object.position.x - 3 <= paddleLeft.object.position.x + 5 && puck.object.position.x - 3 <= paddleLeft.object.position.x && puck.object.position.y <= paddleLeft.object.position.y + 15 && puck.object.position.y >= paddleLeft.object.position.y - 15)
	{
		directionX *= -1
		puck.object.position.x = paddleLeft.object.position.x + 8
		puck.pointLight.position.x = paddleLeft.object.position.x + 8
	}
	if (puck.object.position.y + 3 >= 120 - 5)
		directionY *= -1;
	if (puck.object.position.y - 3 <= -120 + 5)
		directionY *= -1;
	if (puck.object.position.x >= 203 || puck.object.position.x <= -203)
	{
		puck.object.position.x = 0
		puck.pointLight.position.x = 0
	}
}

function puckMouvement()
{
	puck.object.rotation.y += puckSpeed * directionY
	puck.object.position.x += puckSpeed * directionX;
	puck.object.position.y += puckSpeed * directionY;
	puck.pointLight.position.x += puckSpeed * directionX;
	puck.pointLight.position.y += puckSpeed * directionY;
}

function game() {
	requestAnimationFrame( game );
	puckMouvement()
	colision()
	if (windowHeight != window.innerHeight || windowWidth != window.innerWidth)
	{
		threeJS.renderer.setSize( window.innerWidth - 10, window.innerHeight - 200)
		threeJS.camera.position.z = 200;
		threeJS.camera.aspect = (window.innerWidth / window.innerHeight)
		threeJS.camera.updateProjectionMatrix();
		windowHeight == window.innerHeight
		windowWidth == window.innerWidth
	}
	threeJS.renderer.render( threeJS.scene, threeJS.camera );
}


function keyRelease(event)
{
	keyCode[event.which] = false;
}

function keyPress(event)
{
	keyCode[event.which] = true;

	if (keyCode[38] && paddleRight.object.position.y < 96)
		Move.movePaddle("right", 1, paddleLeft, paddleRight);
	if (keyCode[40] && paddleRight.object.position.y > -96)
		Move.movePaddle("right", -1, paddleLeft, paddleRight);
	if (keyCode[87] && paddleLeft.object.position.y < 96)
		Move.movePaddle("left", 1, paddleLeft, paddleRight);
	if (keyCode[83] && paddleLeft.object.position.y > -96)
		Move.movePaddle("left", -1, paddleLeft, paddleRight);
}

game()
