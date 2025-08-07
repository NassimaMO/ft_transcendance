import * as Babylon from "./import.js";
import * as Config from "./config.js"
import * as Obj from "./createObject.js";

// Create the scene //
    /* Create the canvas */
    const canvas = document.getElementById("renderCanvas");
    const engine = new Babylon.Engine(canvas, true);
    var scene = new Babylon.Scene(engine);
    /* Create the background */
    const videoTexture = new Babylon.VideoTexture('background', '/static/pong/media/videoplayback.mp4', scene, true, true, Babylon.VideoTexture.TRILINEAR_SAMPLINGMODE);
    const videoLayer = new Babylon.Layer("videoLayer", null, scene, true);
    videoLayer.texture = videoTexture;
    videoTexture.vScale = -1;
// end //

// Create the loop //
    function renderLoop() { scene.render(); }
    engine.runRenderLoop(renderLoop);
// end //

// Glow effect //
    const gl = new Babylon.GlowLayer("glow", scene);
    gl.intensity = 0.4;
// end //

// Create the camera //
    var cameraRadius = 100;

    if (window.innerWidth / window.innerHeight >= 16 / 7)
        cameraRadius = ((((window.innerWidth / window.innerHeight) / (16 / 7)) * Config.groundLength * Config.groundHeight) * 90) / (Config.groundLength * Config.groundHeight)
    else
        cameraRadius = ((((16 / 7) / (window.innerWidth / window.innerHeight)) * Config.groundLength * Config.groundHeight) * 90) / (Config.groundLength * Config.groundHeight)
    const camera = new Babylon.ArcRotateCamera("camera", 0, Math.PI, -cameraRadius, new Babylon.Vector3(0, 0, 0), scene);
    if (window.innerWidth >= window.innerHeight)
        camera.alpha = 0
    else
        camera.alpha = - Math.PI / 2
// end //

// Make the scene responsive //
    window.addEventListener("resize", () =>
    {
        engine.resize();
        if (window.innerWidth / window.innerHeight >= 16 / 7)
            cameraRadius = ((((window.innerWidth / window.innerHeight) / (16 / 7)) * Config.groundLength * Config.groundHeight) * 90) / (Config.groundLength * Config.groundHeight)
        else
            cameraRadius = ((((16 / 7) / (window.innerWidth / window.innerHeight)) * Config.groundLength * Config.groundHeight) * 90) / (Config.groundLength * Config.groundHeight)
        camera.radius = -cameraRadius
        if (window.innerWidth >= window.innerHeight)
            camera.alpha = 0
        else
            camera.alpha = - Math.PI / 2
    });
// end //

// Create the objects //
    var puck = Obj.puck(scene);
    var leftPaddle = Obj.paddle(Config.groundLength / 3, ((2 - Config.mode) / 8) * Config.groundHeight, Config.paddleColor[0], scene);
    var rightPaddle = Obj.paddle(-Config.groundLength / 3, ((2 - Config.mode) / 8) * Config.groundHeight, Config.paddleColor[1]), scene;
    if (Config.mode == 4) 
    {
        var ndLeftPaddle = Obj.paddle(Config.groundLength / 3, ((Config.mode - 2) / 8) * Config.groundHeight, Config.paddleColor[2], scene);
        var ndRightPaddle = Obj.paddle(-Config.groundLength / 3, ((Config.mode - 2) / 8) * Config.groundHeight, Config.paddleColor[3], scene);
    }
    var upWall = Obj.wall(Config.groundHeight / 2, scene);
    var downWall = Obj.wall(-Config.groundHeight / 2, scene);
    var ground = Obj.ground(scene);
// end //

// Score board //
    var plane = Babylon.MeshBuilder.CreatePlane("plane", { height: 25 , width: 50}, scene);
    var leftPoint = 0;
    var rightPoint = 0;
    var win = 0;

    plane.material = new Babylon.StandardMaterial("mat", scene)
    plane.position.x = 20
    plane.position.y = 0
    plane.rotation.x = Math.PI / 2
    plane.rotation.y = Math.PI / 2
    var dynamicTexture = new Babylon.DynamicTexture("DynamicTexture", {width:512, height:256}, scene, true);
    dynamicTexture.drawText(leftPoint + " - " + rightPoint, null, null, "120px Minecraft", "white", "transparent", true, true);
    plane.material.emissiveTexture = dynamicTexture;
    plane.material.maxSimultaneousLights = 12;
// end //

// Puck Mouvement //
    var directionX = 1;
    var directionZ = 1;

    function scorePoint(player, point)
    {
        puck.position.x = 0;
        puck.position.z = 0;
        if (player === "Right")
            rightPoint += 1;
        if (player === "Left")
            leftPoint += 1;
        dynamicTexture.dispose();
        dynamicTexture = new Babylon.DynamicTexture("DynamicTexture", {width:512, height:256}, scene, true);
        /* If the player has 10 point, he win */
        if (point == 9)
        {
            dynamicTexture.drawText(player + " player has won", null, null, "45px Minecraft", "white", "transparent", true, true);
            win = 1;
        }
        /* Otherwise update the score */
        else
            dynamicTexture.drawText(leftPoint + " - " + rightPoint, null, null, "120px Minecraft", "white", "transparent", true, true);
        plane.material.emissiveTexture = dynamicTexture;
    }

    scene.registerBeforeRender(() => 
    {
        if (win === 0)
        {
            /* If the puck touch a wall */
            if (puck.position.x >= (Config.groundHeight / 2 ) - 2.5 || puck.position.x <= - (Config.groundHeight / 2) + 2.5)
            {
                directionX *= -1
                puck.position.x += 1 * directionX;
            }
            /* If the left player score */
            if (puck.position.z <= - Config.groundLength / 2)
                scorePoint("Left", leftPoint);
            /* If the right player score */
            if (puck.position.z >= Config.groundLength / 2)
                scorePoint("Right", rightPoint);
            /* If the puck touch a paddle */
            if ((puck.intersectsMesh(leftPaddle, true) || puck.intersectsMesh(rightPaddle, true)) && !(puck.position.z > (Config.groundLength  / 3 - 2.5)) && !((puck.position.z < -Config.groundLength  / 3 + 2.5)))
                directionZ *= -1
            puck.position.x += Config.puckSpeed * directionX;
            puck.position.z += Config.puckSpeed * directionZ;
        }
    });
// end //

// Movement of the paddles //
    const keys = { w: false, s: false, up: false, down: false };

    window.addEventListener("keydown", (e) => { switch (e.code) 
    {
        /* Press left paddle key */
        case "KeyW": keys.w = true; break;
        case "KeyS": keys.s = true; break;
        /* Press right paddle key */
        case "ArrowUp": keys.up = true; break;
        case "ArrowDown": keys.down = true; break;
    }
    });
    window.addEventListener("keyup", (e) => { switch (e.code) 
    {
        /* Release left paddle key */
        case "KeyW": keys.w = false; break;
        case "KeyS": keys.s = false; break;
        /* Release right paddle key */
        case "ArrowUp": keys.up = false; break;
        case "ArrowDown": keys.down = false; break;
    }
    });
    /* Move the paddle if a key is press */
    scene.onBeforeRenderObservable.add(() => 
    {
        if (keys.w && leftPaddle.position.x < (Config.groundHeight / 2) - (Config.paddleSize[1] / 2) - 2) leftPaddle.position.x += Config.paddleSpeed;
        if (keys.s && leftPaddle.position.x > -(Config.groundHeight / 2) + (Config.paddleSize[1] / 2) + 2) leftPaddle.position.x -= Config.paddleSpeed;
        if (keys.up && rightPaddle.position.x < (Config.groundHeight / 2) - (Config.paddleSize[1] / 2) - 2) rightPaddle.position.x += Config.paddleSpeed;
        if (keys.down && rightPaddle.position.x > -(Config.groundHeight / 2) + (Config.paddleSize[1] / 2) + 2) rightPaddle.position.x -= Config.paddleSpeed;
    });
// end //