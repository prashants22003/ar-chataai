// Lightweight three.js preview with KTX2 support

import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'https://unpkg.com/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';
import { KTX2Loader } from 'https://unpkg.com/three@0.160.0/examples/jsm/loaders/KTX2Loader.js';

class ThreePreview {
    constructor() {
        this.container = null;
        this.canvas = null;
        this.renderer = null;
        this.scene = null;
        this.camera = null;
        this.controls = null;
        this.gltfLoader = null;
        this.animId = null;
        this.model = null;
        this.initialized = false;
    }

    init(containerSelector = '.model-viewer-container') {
        if (this.initialized) return;

        this.container = document.querySelector(containerSelector);
        if (!this.container) return;

        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.container.appendChild(this.renderer.domElement);

        // Scene & camera
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(45, this.container.clientWidth / this.container.clientHeight, 0.1, 100);
        this.camera.position.set(2.5, 2.0, 2.5);

        // Controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;

        // Lights
        const hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 1.0);
        hemi.position.set(0, 1, 0);
        this.scene.add(hemi);
        const dir = new THREE.DirectionalLight(0xffffff, 1.0);
        dir.position.set(3, 5, 2);
        this.scene.add(dir);

        // Loaders
        const ktx2 = new KTX2Loader()
            .setTranscoderPath('https://unpkg.com/three@0.160.0/examples/jsm/libs/basis/')
            .detectSupport(this.renderer);
        this.gltfLoader = new GLTFLoader();
        this.gltfLoader.setKTX2Loader(ktx2);

        window.addEventListener('resize', () => this.onResize());

        this.initialized = true;
        this.animate();
    }

    async loadModel(url) {
        if (!this.initialized) this.init();
        // Clear previous model
        if (this.model) {
            this.scene.remove(this.model);
            this.model.traverse((o) => {
                if (o.isMesh) {
                    o.geometry.dispose();
                    if (o.material.map) o.material.map.dispose();
                    if (o.material.normalMap) o.material.normalMap.dispose();
                }
            });
            this.model = null;
        }

        return new Promise((resolve, reject) => {
            this.gltfLoader.load(
                url,
                (gltf) => {
                    this.model = gltf.scene;
                    this.scene.add(this.model);
                    this.frameModel();
                    resolve();
                },
                undefined,
                (err) => reject(err)
            );
        });
    }

    frameModel() {
        const box = new THREE.Box3().setFromObject(this.model);
        const size = new THREE.Vector3();
        const center = new THREE.Vector3();
        box.getSize(size);
        box.getCenter(center);

        const maxDim = Math.max(size.x, size.y, size.z);
        const dist = maxDim * 1.8;
        this.camera.position.set(center.x + dist, center.y + dist, center.z + dist);
        this.controls.target.copy(center);
        this.controls.update();
    }

    onResize() {
        if (!this.container) return;
        const w = this.container.clientWidth;
        const h = this.container.clientHeight;
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
    }

    animate() {
        this.animId = requestAnimationFrame(() => this.animate());
        if (this.controls) this.controls.update();
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }
}

window.threePreview = new ThreePreview();


