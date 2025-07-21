import * as Babylon from "./import.js";
import * as Config from "./config.js"
import * as Obj from "./createObject.js";

// Create the scene //
const canvas = document.getElementById("renderCanvas");
const engine = new Babylon.Engine(canvas, true);
var scene = new Babylon.Scene(engine);

// Create the loop //
function renderLoop() { scene.render(); }
engine.runRenderLoop(renderLoop);

// Create the camera //
const camera = new Babylon.ArcRotateCamera("camera", 0, Math.PI , -Config.groundHeight / 1.7, new Babylon.Vector3(0, 0, 0), scene);

// Create the objects //
var puck = Obj.puck(scene);
var leftPaddle = Obj.paddle(Config.groundHeight / 3, ((2 - Config.mode) / 8) * Config.groundWidth, Config.paddleColor[0], scene);
var rightPaddle = Obj.paddle(-Config.groundHeight / 3, ((2 - Config.mode) / 8) * Config.groundWidth, Config.paddleColor[1]), scene;
if (Config.mode == 4) 
{
    var ndLeftPaddle = Obj.paddle(Config.groundHeight / 3, ((Config.mode - 2) / 8) * Config.groundWidth, Config.paddleColor[2], scene);
    var ndRightPaddle = Obj.paddle(-Config.groundHeight / 3, ((Config.mode - 2) / 8) * Config.groundWidth, Config.paddleColor[3], scene);
}
const ground = Babylon.MeshBuilder.CreateGround("ground", {width: Config.groundWidth, height: Config.groundHeight}, scene);
