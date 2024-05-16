import * as THREE from 'three';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );

const renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );

var textureLoader = new THREE.TextureLoader();
var lightMap = textureLoader.load('texture.jpg');

const geometrySphere = new THREE.SphereGeometry( 1, 64, 64 );
const materialSphere = new THREE.MeshStandardMaterial( { color: 0x00ff00, lightMap: lightMap, lightMapIntensity: 5} );
const ball = new THREE.Mesh( geometrySphere, materialSphere );
scene.add( ball );

const geometryPaddle = new THREE.BoxGeometry( 10, 30, 5 );
const materialPaddle = new THREE.MeshStandardMaterial( { color: 0xff0000, lightMap: lightMap, lightMapIntensity: 5} );
const paddle = new THREE.Mesh( geometryPaddle, materialPaddle );
paddle.position.x = -20
scene.add( paddle );

const geometryTable = new THREE.BoxGeometry( 100, 100, 1 );
const materialTable = new THREE.MeshStandardMaterial( { color: 0xffffff} );
const table = new THREE.Mesh( geometryTable, materialTable );
table.position.z = -5
scene.add( table );

const pointLight = new THREE.PointLight( 0x00ff00, 10);
scene.add( pointLight );

const pointLight2 = new THREE.PointLight( 0xff0000, 100);
pointLight2.position.set( -20, 0, 0 );
scene.add( pointLight2 );

const lighthelper = new THREE.PointLightHelper(pointLight)
scene.add(lighthelper)


//const light = new THREE.AmbientLight( 0xffffff ); // soft white light
//scene.add( light );

camera.position.z = 50;

function animate() {
	requestAnimationFrame( animate );

	//ball.rotation.x -= 0.1
	ball.rotation.y -= 0.1
	ball.position.x -= 0.01;
	pointLight.position.x -= 0.01;
	//sphere.position.y -= 0.01;

	renderer.render( scene, camera );
}

animate();
