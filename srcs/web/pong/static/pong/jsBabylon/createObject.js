import * as Babylon from "./import.js";
import * as Config from "./config.js";

export function puck(scene)
{
    var puck = Babylon.MeshBuilder.CreateCylinder("puck", { diameter: Config.puckDiameter}, scene);
    puck.position.y = 1;
    puck.material = new Babylon.StandardMaterial("mat", scene);
    puck.material.maxSimultaneousLights = 12;
    puck.material.emissiveColor = new Babylon.Color3(0, 1, 0);
    puck.enableEdgesRendering();
    puck.edgesWidth = 5.0;
    puck.edgesColor = new Babylon.Color4(0, 0, 0, 1);

    var light = new Babylon.PointLight("light", puck.position, scene);
    light.diffuse = new Babylon.Color3(0, 1, 0);
    light.range = 60;
    
    return (puck);
}

function paddleLight(paddle, paddleZ, paddleX, paddleColor, scene)
{
    const light = new Babylon.PointLight("light", paddle.position, scene);
    light.parent = paddle;
    light.diffuse = Babylon.Color3.FromHexString(paddleColor);
    light.position = new Babylon.Vector3(paddleX, 0, (paddleZ / Math.abs(paddleZ)) * 3);
    light.intensity = 0.5
    light.range = 60;

    return (light);
}

export function paddle(paddleZ, paddleX, paddleColor, scene)
{
    var paddle = Babylon.MeshBuilder.CreateBox("paddle", { size: Config.paddleSize[0], width: Config.paddleSize[1]}, scene);
    paddle.position.z = paddleZ;
    paddle.position.y = 5;
    paddle.position.x = paddleX;
    paddle.material = new Babylon.StandardMaterial("mat", scene);
    paddle.material.maxSimultaneousLights = 8;
    paddle.material.emissiveColor = Babylon.Color3.FromHexString(paddleColor);
    paddle.enableEdgesRendering();
    paddle.edgesWidth = 20.0;
    paddle.edgesColor = new Babylon.Color4(0, 0, 0, 1);

    const upLight = paddleLight(paddle, paddleZ, Config.paddleSize[0], paddleColor, scene);
    const downLight = paddleLight(paddle, paddleZ, -Config.paddleSize[0], paddleColor, scene);
    //const middleLight = paddleLight(paddle, paddleZ, 0, paddleColor, scene);

    return (paddle);
}

export function wall(wallX, scene)
{
    var wall = Babylon.MeshBuilder.CreateBox("wall", { height: 7.5, width: 2 , depth: Config.groundLength - 5 }, scene);
    wall.position.x = wallX;
    wall.position.y = 3.75;
    wall.material = new Babylon.StandardMaterial("mat", scene);
    wall.material.maxSimultaneousLights = 8;
    wall.enableEdgesRendering();
    wall.edgesWidth = 20.0;
    wall.edgesColor = new Babylon.Color4(0, 0, 0, 1);
    
    /*var face = Babylon.MeshBuilder.CreatePlane("face", { height: Config.groundLength - 5 , width: 2}, scene);
    face.material = new Babylon.StandardMaterial("mat", scene)
    face.position.y = 2.5;
    face.rotation.x = Math.PI / 2
    face.parent = wall;
    face.material.emissiveColor = new Babylon.Color3(1,0,1);*/

    var face = Babylon.MeshBuilder.CreatePlane("face", { height: (Config.groundLength / 2) - 2.5 , width: 2}, scene);
    face.material = new Babylon.StandardMaterial("mat", scene)
    face.position.y = 5;
    face.position.z = -(Config.groundLength / 4) + 1.25
    face.rotation.x = Math.PI / 2
    face.parent = wall;
    face.material.emissiveColor = new Babylon.Color3(1,0,0);
    var face2 = Babylon.MeshBuilder.CreatePlane("face2", { height: (Config.groundLength / 2) - 2.5 , width: 2}, scene);
    face2.material = new Babylon.StandardMaterial("mat", scene)
    face2.position.y = 5;
    face2.position.z = (Config.groundLength / 4) - 1
    face2.rotation.x = Math.PI / 2
    face2.parent = wall;
    face2.material.emissiveColor = new Babylon.Color3(0,0,1);

    //wall.emissiveTexture = new Babylon.Texture("/static/pong/media/degrade.jpg", scene);
    //wall.material.emissiveColor = new Babylon.Color3(1,0,1);
   
    
    const rightLight = new Babylon.PointLight("rightLight", new Babylon.Vector3(wallX ,25 ,-(Config.groundLength/2) - 20), scene);
    rightLight.diffuse = new Babylon.Color3(0,0,1);
    rightLight.intensity = 0.4
    
    const leftLight = new Babylon.PointLight("leftLight", new Babylon.Vector3(wallX ,25 ,(Config.groundLength/2) + 20), scene);
    leftLight.diffuse = new Babylon.Color3(1,0,0);
    leftLight.intensity = 0.4
/*
    const middleLight = new Babylon.PointLight("middleLight", new Babylon.Vector3(wallX + (20 * (wallX / Math.abs(wallX))) ,25 ,0), scene);
    middleLight.diffuse = new Babylon.Color3(1,0,1);
    middleLight.intensity = 0.4
    
    return (wall);*/
}

export function ground(scene)
{
    const ground = Babylon.MeshBuilder.CreateGround("ground", {width: Config.groundHeight, height: Config.groundLength}, scene);
    ground.material = new Babylon.StandardMaterial("mat", scene);
    ground.material.maxSimultaneousLights = 12;

    const dynTex = new Babylon.DynamicTexture("gridTex", { width: Config.groundHeight * 2, height: Config.groundLength * 2}, scene, false);
    const ctx = dynTex.getContext();

    // Quadrillage gris
    ctx.strokeStyle = "rgba(50, 0, 50, 1)";
    ctx.lineWidth = 1;

    for (let i = 0; i <= Config.groundLength * 2; i += 20) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, Config.groundLength * 2);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(Config.groundLength * 2, i);
        ctx.stroke();
    }

    dynTex.update();

    // Matériau standard avec lumière
    ground.material.emissiveTexture = dynTex;
    ground.material.specularColor = new Babylon.Color3(0.3, 0.3, 0.3); // reflet doux
    ground.material.backFaceCulling = false;
}