import * as Babylon from "./import.js";
import * as Config from "./config.js";

export function puck(scene)
{
    var puck = Babylon.MeshBuilder.CreateCylinder("puck", { diameter: Config.puckDiameter}, scene);
    puck.position.y = 1;
    puck.material = new Babylon.StandardMaterial("mat", scene);
    puck.material.emissiveColor = new Babylon.Color3(0, 1, 0);
    var light = new Babylon.PointLight("light", puck.position, scene);
    light.diffuse = new Babylon.Color3(0, 1, 0);
    light.intensity = 2;
    
    return (puck);
}

export function paddle(paddleZ, paddleX, paddleColor, scene)
{
    var paddle = Babylon.MeshBuilder.CreateBox("paddle", { size: 5, width: Config.paddleSize[1]}, scene);
    paddle.position.z = paddleZ;
    paddle.position.y = 5;
    paddle.position.x = paddleX;
    paddle.material = new Babylon.StandardMaterial("mat", scene);
    paddle.material.emissiveColor = new Babylon.Color3(paddleColor);
    const light = new Babylon.RectAreaLight("area", new Babylon.Vector3(5, 0, 0), Config.paddleSize[1], Config.paddleSize[0], scene);
    light.parent = paddle;
    light.diffuse = new Babylon.Color3(1, 0, 0);
    light.intensity = 2;
    paddle.rotation.x = - Math.PI / 2

    
    return (paddle);
}