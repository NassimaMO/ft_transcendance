import * as THREE from 'three';
import { OrbitControls } from 'orbitcontrols';
import * as Object from './buildObject.js'

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );

const renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );

let ball = Object.puck()
let paddleLeft = Object.paddle(-180, 0, 0)
let paddleRight = Object.paddle(180, 0, 0)
scene.add( paddleLeft.object, paddleLeft.rectLight, paddleRight.object, paddleRight.rectLight, ball.object, ball.pointLight);

const geometryTable = new THREE.BoxGeometry( 427, 240, 1 );
const materialTable = new THREE.MeshStandardMaterial( { color: 0xffffff} );
const table = new THREE.Mesh( geometryTable, materialTable );
table.position.z = -4
//table.metalness = 1
scene.add( table );

let wallLeft = Object.wallVertical(-213, 0, 0)
scene.add(wallLeft.object, wallLeft.rectLight)

let wallRight = Object.wallVertical(213, 0, 0)
scene.add(wallRight.object, wallRight.rectLight)

let wallUp = Object.wallHorizontal(0, 120, 0)
scene.add(wallUp.object, wallUp.rectLight)

let wallDown = Object.wallHorizontal(0, -120, 0)
scene.add(wallDown.object, wallDown.rectLight)

//const light = new THREE.AmbientLight( 0xffffff ); // soft white light
//scene.add( light );

camera.position.z = 200;

const controls = new OrbitControls(camera, renderer.domElement)

let direction = 1;

function colision()
{
	if (ball.object.position.x + 2.5 >= paddleRight.object.position.x - 5 && ball.object.position.y <= paddleRight.object.position.y + 15 && ball.object.position.y >= paddleRight.object.position.y - 15)
		direction *= -1
	if (ball.object.position.x - 2.5 <= paddleLeft.object.position.x + 5)
		direction *= -1
	if (ball.object.position.x >= 203)
	{
		ball.object.position.x = 0
		ball.pointLight.position.x = 0
	}
}

function ballMouvement()
{
	ball.object.rotation.y += 1 * direction
	ball.object.position.x += 1 * direction;
	ball.pointLight.position.x += 1 *direction;
}

function game() {
	requestAnimationFrame( game );
	ballMouvement()
	colision()
	renderer.render( scene, camera );
}

document.addEventListener("keydown", onDocumentKeyDown, false);
function onDocumentKeyDown(event)
{
	var keyCode = event.which;
	if (keyCode === 38 && paddleRight.object.position.y < 95)
	{
		paddleRight.object.position.y += 1
		paddleRight.rectLight.position.y += 1
	}
	else if (event.keyCode === 40 && paddleRight.object.position.y > -95)
	{
		paddleRight.object.position.y -= 1
		paddleRight.rectLight.position.y -= 1
	}
}

game();
