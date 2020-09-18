/**
 * Copyright 2018, Google LLC
 * Licensed under the Apache License, Version 2.0 (the `License`);
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an `AS IS` BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// [START gae_python38_log]
'use strict';

import * as THREE from '../static/node_modules/three/build/three.module.js';
import {OrbitControls} from '../static/node_modules/three/examples/jsm/controls/OrbitControls.js';

var container;
var camera, controls, scene, renderer;
var mesh, texture;

var scale, margin;

var worldWidth = 252, worldDepth = 252;

window.addEventListener('load', function () {

  init();
  animate();

});

function init() {

    container = document.getElementById('container');

    // FOV, aspect, near, far
    camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 1, 5000);

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xCDF0FF);

    camera.position.y = 200;
    camera.position.x = 300;
    camera.position.z = 200;

    margin = 2;
    scale = 0.7;

    var geometry = new THREE.PlaneBufferGeometry(256-2*margin, 256-2*margin, worldWidth-1, worldDepth-1);
    geometry.rotateX(-Math.PI / 2);

    var vertices = geometry.attributes.position.array;
    for (var i = 0; i < vertices.length; i ++) {
        vertices[3*i + 1] = heights[i];
    }

    // FIXME
    texture = new THREE.TextureLoader().load('/img/trimmed.png');
    texture.wrapS = THREE.ClampToEdgeWrapping;
    texture.wrapT = THREE.ClampToEdgeWrapping;

    mesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({map: texture, side: THREE.DoubleSide}));
    scene.add(mesh);

    renderer = new THREE.WebGLRenderer();
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(scale * window.innerWidth, scale * window.innerHeight);
    container.appendChild( renderer.domElement);

    controls = new OrbitControls(camera, renderer.domElement);

    window.addEventListener('resize', onWindowResize, false);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(scale * window.innerWidth, scale * window.innerHeight);
}

function animate() {
    requestAnimationFrame(animate);
    render();
}

function render() {
    renderer.render(scene, camera);
}

// [END gae_python38_log]
