import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Html, Line } from "@react-three/drei";
import { useMemo, useRef } from "react";
import * as THREE from "three";

import Earth from "./Earth";
import ScanBeam from "./ScanBeam";

interface MissionSceneProps {
    onMissionComplete?: () => void;
}

/* ============================================================
   GLYAB MISSION CONFIGURATION
============================================================ */

const TARGET_LATITUDE = 30.421;
const TARGET_LONGITUDE = 79.208;
const TARGET_ALTITUDE = 4870;

const EARTH_RADIUS = 2.5;


/* ============================================================
   GEO COORDINATE → THREE VECTOR
============================================================ */

function latLonToVector3(
    latitude: number,
    longitude: number,
    radius: number,
) {
    const phi =
        (90 - latitude) *
        Math.PI /
        180;

    const theta =
        (longitude + 180) *
        Math.PI /
        180;

    return new THREE.Vector3(
        -radius *
        Math.sin(phi) *
        Math.cos(theta),

        radius *
        Math.cos(phi),

        radius *
        Math.sin(phi) *
        Math.sin(theta),
    );
}


/* ============================================================
   STAR FIELD
============================================================ */

function StarField() {
    const stars = useMemo(() => {
        return Array.from(
            { length: 1100 },
            (_, index) => {
                const radius =
                    18 +
                    Math.random() * 45;

                const theta =
                    Math.random() *
                    Math.PI *
                    2;

                const phi =
                    Math.acos(
                        2 *
                        Math.random() -
                        1,
                    );

                return {
                    index,

                    position: [
                        radius *
                        Math.sin(phi) *
                        Math.cos(theta),

                        radius *
                        Math.cos(phi),

                        radius *
                        Math.sin(phi) *
                        Math.sin(theta),
                    ] as [
                            number,
                            number,
                            number,
                        ],

                    size:
                        0.006 +
                        Math.random() *
                        0.018,
                };
            },
        );
    }, []);

    return (
        <group>
            {stars.map((star) => (
                <mesh
                    key={star.index}
                    position={
                        star.position
                    }
                >
                    <sphereGeometry
                        args={[
                            star.size,
                            5,
                            5,
                        ]}
                    />

                    <meshBasicMaterial
                        color="#bdefff"
                    />
                </mesh>
            ))}
        </group>
    );
}


/* ============================================================
   SATELLITE
============================================================ */

function OrbitalSatellite() {
    const satellite =
        useRef<THREE.Group>(null);

    useFrame(({ clock }) => {
        if (!satellite.current) {
            return;
        }

        const time =
            clock.getElapsedTime();

        const radius = 4.25;

        const speed = 0.22;

        satellite.current.position.x =
            Math.cos(
                time * speed,
            ) *
            radius;

        satellite.current.position.z =
            Math.sin(
                time * speed,
            ) *
            radius;

        satellite.current.position.y =
            Math.sin(
                time *
                speed *
                1.7,
            ) *
            0.72;

        satellite.current.rotation.y =
            time * 0.35;

        satellite.current.lookAt(
            0,
            0,
            0,
        );
    });

    return (
        <group
            ref={satellite}
            scale={0.32}
        >

            {/* BODY */}

            <mesh>
                <boxGeometry
                    args={[
                        1.45,
                        0.65,
                        0.9,
                    ]}
                />

                <meshStandardMaterial
                    color="#c8d5df"
                    metalness={0.9}
                    roughness={0.22}
                />
            </mesh>


            {/* LEFT SOLAR PANEL */}

            <mesh
                position={[
                    -1.35,
                    0,
                    0,
                ]}
            >
                <boxGeometry
                    args={[
                        1.9,
                        0.06,
                        0.95,
                    ]}
                />

                <meshStandardMaterial
                    color="#102c4d"
                    metalness={0.7}
                    roughness={0.2}
                />
            </mesh>


            {/* RIGHT SOLAR PANEL */}

            <mesh
                position={[
                    1.35,
                    0,
                    0,
                ]}
            >
                <boxGeometry
                    args={[
                        1.9,
                        0.06,
                        0.95,
                    ]}
                />

                <meshStandardMaterial
                    color="#102c4d"
                    metalness={0.7}
                    roughness={0.2}
                />
            </mesh>


            {/* PANEL LINES */}

            <mesh
                position={[
                    -1.35,
                    0.04,
                    0,
                ]}
            >
                <boxGeometry
                    args={[
                        0.025,
                        0.08,
                        0.95,
                    ]}
                />

                <meshBasicMaterial
                    color="#6eeaff"
                />
            </mesh>

            <mesh
                position={[
                    1.35,
                    0.04,
                    0,
                ]}
            >
                <boxGeometry
                    args={[
                        0.025,
                        0.08,
                        0.95,
                    ]}
                />

                <meshBasicMaterial
                    color="#6eeaff"
                />
            </mesh>


            {/* SENSOR */}

            <mesh
                position={[
                    0,
                    -0.56,
                    0,
                ]}
            >
                <cylinderGeometry
                    args={[
                        0.2,
                        0.28,
                        0.38,
                        32,
                    ]}
                />

                <meshStandardMaterial
                    color="#172630"
                    metalness={0.9}
                    roughness={0.12}
                />
            </mesh>


            {/* SENSOR LENS */}

            <mesh
                position={[
                    0,
                    -0.78,
                    0,
                ]}
            >
                <sphereGeometry
                    args={[
                        0.13,
                        24,
                        24,
                    ]}
                />

                <meshStandardMaterial
                    color="#00eaff"
                    emissive="#00eaff"
                    emissiveIntensity={7}
                />
            </mesh>


            {/* ANTENNA */}

            <mesh
                position={[
                    0,
                    0.7,
                    0,
                ]}
            >
                <cylinderGeometry
                    args={[
                        0.035,
                        0.035,
                        0.9,
                        16,
                    ]}
                />

                <meshStandardMaterial
                    color="#d8e1e8"
                    metalness={0.8}
                    roughness={0.2}
                />
            </mesh>


            {/* COMMUNICATION DISH */}

            <mesh
                position={[
                    0,
                    1.18,
                    0,
                ]}
            >
                <sphereGeometry
                    args={[
                        0.34,
                        32,
                        16,
                        0,
                        Math.PI * 2,
                        0,
                        Math.PI / 2,
                    ]}
                />

                <meshStandardMaterial
                    color="#dce6ee"
                    metalness={0.75}
                    roughness={0.18}
                />
            </mesh>


            {/* NAVIGATION LIGHT */}

            <mesh
                position={[
                    0.68,
                    0.38,
                    0.48,
                ]}
            >
                <sphereGeometry
                    args={[
                        0.065,
                        16,
                        16,
                    ]}
                />

                <meshStandardMaterial
                    color="#42ff9b"
                    emissive="#42ff9b"
                    emissiveIntensity={7}
                />
            </mesh>

        </group>
    );
}


/* ============================================================
   SATELLITE GROUND TRACK
============================================================ */

function GroundTrack() {
    const points =
        useMemo(() => {
            const result: THREE.Vector3[] =
                [];

            for (
                let i = 0;
                i <= 180;
                i++
            ) {
                const t =
                    (i / 180) *
                    Math.PI *
                    2;

                result.push(
                    new THREE.Vector3(
                        Math.cos(t) *
                        4.25,

                        Math.sin(
                            t * 1.7,
                        ) *
                        0.72,

                        Math.sin(t) *
                        4.25,
                    ),
                );
            }

            return result;
        }, []);

    return (
        <Line
            points={points}
            color="#38d9ff"
            transparent
            opacity={0.22}
            lineWidth={1}
        />
    );
}


/* ============================================================
   TARGET ACQUISITION
============================================================ */

function TargetAcquisition() {
    const target =
        useRef<THREE.Group>(null);

    const ring =
        useRef<THREE.Mesh>(null);

    const pulse =
        useRef<THREE.Mesh>(null);

    const targetPosition =
        useMemo(
            () =>
                latLonToVector3(
                    TARGET_LATITUDE,
                    TARGET_LONGITUDE,
                    EARTH_RADIUS +
                    0.055,
                ),
            [],
        );

    useFrame(({ clock }) => {
        const time =
            clock.getElapsedTime();

        if (target.current) {
            target.current.rotation.y =
                Math.sin(
                    time * 1.3,
                ) *
                0.08;
        }

        if (ring.current) {
            ring.current.rotation.z =
                time * 1.8;
        }

        if (pulse.current) {
            const scale =
                1 +
                Math.sin(
                    time * 4,
                ) *
                0.35;

            pulse.current.scale.set(
                scale,
                scale,
                scale,
            );

            const material =
                pulse.current
                    .material as THREE.MeshBasicMaterial;

            material.opacity =
                0.12 +
                (Math.sin(
                    time * 4,
                ) +
                    1) *
                0.08;
        }
    });

    return (
        <group ref={target}>
            <group
                position={
                    targetPosition
                }
            >

                {/* PULSE */}

                <mesh ref={pulse}>
                    <sphereGeometry
                        args={[
                            0.16,
                            24,
                            24,
                        ]}
                    />

                    <meshBasicMaterial
                        color="#ff3045"
                        transparent
                        opacity={0.2}
                        depthWrite={false}
                    />
                </mesh>


                {/* CORE */}

                <mesh>
                    <sphereGeometry
                        args={[
                            0.045,
                            24,
                            24,
                        ]}
                    />

                    <meshStandardMaterial
                        color="#ff3045"
                        emissive="#ff3045"
                        emissiveIntensity={9}
                    />
                </mesh>


                {/* TARGET RING */}

                <mesh
                    ref={ring}
                    rotation={[
                        Math.PI / 2,
                        0,
                        0,
                    ]}
                >
                    <torusGeometry
                        args={[
                            0.14,
                            0.012,
                            16,
                            48,
                        ]}
                    />

                    <meshBasicMaterial
                        color="#ff3045"
                    />
                </mesh>


                {/* TARGET HUD */}

                <Html
                    distanceFactor={7}
                    position={[
                        0.17,
                        0.2,
                        0,
                    ]}
                >
                    <div
                        style={{
                            width: "225px",
                            padding:
                                "12px 14px",

                            background:
                                "rgba(2,10,16,.9)",

                            border:
                                "1px solid rgba(255,60,75,.55)",

                            boxShadow:
                                "0 0 28px rgba(255,40,60,.16)",

                            color: "#e9faff",

                            fontFamily:
                                "Arial, sans-serif",

                            pointerEvents:
                                "none",
                        }}
                    >
                        <div
                            style={{
                                color: "#ff4050",
                                fontSize:
                                    "9px",
                                letterSpacing:
                                    "2px",
                                marginBottom:
                                    "8px",
                            }}
                        >
                            ● TARGET ACQUISITION
                        </div>

                        <div
                            style={{
                                fontSize:
                                    "12px",
                                fontWeight:
                                    700,
                                letterSpacing:
                                    "1px",
                            }}
                        >
                            HIMALAYAN SECTOR
                        </div>

                        <div
                            style={{
                                marginTop:
                                    "8px",
                                fontSize:
                                    "9px",
                                color:
                                    "#7fa5b5",
                                lineHeight:
                                    "1.8",
                            }}
                        >
                            LAT&nbsp;&nbsp;
                            {TARGET_LATITUDE.toFixed(
                                3,
                            )}
                            ° N
                            <br />

                            LON&nbsp;&nbsp;
                            {TARGET_LONGITUDE.toFixed(
                                3,
                            )}
                            ° E
                            <br />

                            ALT&nbsp;&nbsp;
                            {TARGET_ALTITUDE.toLocaleString()}{" "}
                            m
                        </div>

                        <div
                            style={{
                                marginTop:
                                    "9px",
                                color:
                                    "#4dff9a",
                                fontSize:
                                    "8px",
                                letterSpacing:
                                    "1.4px",
                            }}
                        >
                            TARGET LOCK · GEOREFERENCE READY
                        </div>
                    </div>
                </Html>
            </group>
        </group>
    );
}


/* ============================================================
   CINEMATIC CAMERA
============================================================ */

function CameraController({
    onComplete,
}: {
    onComplete?: () => void;
}) {
    const { camera } =
        useThree();

    const elapsed =
        useRef(0);

    const completed =
        useRef(false);

    const target =
        useMemo(
            () =>
                latLonToVector3(
                    TARGET_LATITUDE,
                    TARGET_LONGITUDE,
                    EARTH_RADIUS +
                    0.04,
                ),
            [],
        );

    const rotatedTarget =
        useMemo(
            () =>
                new THREE.Vector3(),
            [],
        );

    const axis =
        useMemo(
            () =>
                new THREE.Vector3(
                    0,
                    1,
                    0,
                ),
            [],
        );

    const cameraStart =
        useMemo(
            () =>
                new THREE.Vector3(
                    4.6,
                    2.5,
                    4.6,
                ),
            [],
        );

    const cameraEnd =
        useMemo(
            () =>
                new THREE.Vector3(
                    3.35,
                    1.85,
                    3.35,
                ),
            [],
        );

    useFrame((_, delta) => {
        elapsed.current +=
            delta;

        const time =
            elapsed.current;

        /* ---------------------------------
           PHASE 1 — DEEP SPACE
        --------------------------------- */

        if (time < 4) {
            const progress =
                time / 4;

            camera.position.set(
                0,
                0.3,
                11 -
                progress *
                1.5,
            );

            camera.lookAt(
                0,
                0,
                0,
            );

            return;
        }


        /* ---------------------------------
           PHASE 2 — EARTH APPROACH
        --------------------------------- */

        if (time < 9) {
            const progress =
                (time - 4) / 5;

            camera.position.set(
                0.2,
                0.5,
                9.5 -
                progress *
                3.8,
            );

            camera.lookAt(
                0,
                0,
                0,
            );

            return;
        }


        /* ---------------------------------
           PHASE 3 — ORBITAL OBSERVATION
        --------------------------------- */

        if (time < 14) {
            const progress =
                (time - 9) / 5;

            const angle =
                progress *
                Math.PI *
                0.45;

            camera.position.set(
                Math.sin(angle) *
                5.8,

                1.5 +
                progress *
                0.8,

                Math.cos(angle) *
                5.8,
            );

            camera.lookAt(
                0,
                0,
                0,
            );

            return;
        }


        /* ---------------------------------
           PHASE 4 — TARGET LOCK
        --------------------------------- */

        const progress =
            Math.min(
                (time - 14) / 6,
                1,
            );

        rotatedTarget
            .copy(target)
            .applyAxisAngle(
                axis,
                (time - 14) *
                0.035,
            );

        camera.position.lerpVectors(
            cameraStart,
            cameraEnd,
            progress,
        );

        camera.lookAt(
            rotatedTarget,
        );


        /* ---------------------------------
           MISSION COMPLETE
        --------------------------------- */

        if (
            progress >= 1 &&
            !completed.current
        ) {
            completed.current = true;

            if (onComplete) {
                window.setTimeout(
                    () => {
                        onComplete();
                    },
                    1200,
                );
            }
        }
    });

    return null;
}


/* ============================================================
   MISSION HUD
============================================================ */

function MissionHUD({
    onSkip,
}: {
    onSkip?: () => void;
}) {
    return (
        <div
            style={{
                position: "absolute",
                inset: 0,
                zIndex: 10,
                pointerEvents:
                    "none",
                color: "#dffaff",
                fontFamily:
                    "Inter, Segoe UI, sans-serif",
            }}
        >

            {/* TOP LEFT */}

            <div
                style={{
                    position:
                        "absolute",
                    top: "28px",
                    left: "32px",
                }}
            >
                <div
                    style={{
                        fontSize:
                            "19px",
                        fontWeight:
                            700,
                        letterSpacing:
                            "4px",
                    }}
                >
                    GLYAB
                    <span
                        style={{
                            color:
                                "#51e5ff",
                        }}
                    >
                        {" "}
                        AI
                    </span>
                </div>

                <div
                    style={{
                        marginTop:
                            "6px",
                        fontSize:
                            "8px",
                        letterSpacing:
                            "2px",
                        color:
                            "#608795",
                    }}
                >
                    CRYOSPHERE INTELLIGENCE
                </div>
            </div>


            {/* TOP RIGHT */}

            <div
                style={{
                    position:
                        "absolute",
                    top: "28px",
                    right: "32px",
                    textAlign:
                        "right",
                }}
            >
                <div
                    style={{
                        fontSize:
                            "8px",
                        letterSpacing:
                            "2px",
                        color:
                            "#5e7c86",
                    }}
                >
                    MISSION STATUS
                </div>

                <div
                    style={{
                        marginTop:
                            "6px",
                        color:
                            "#4dff9a",
                        fontSize:
                            "9px",
                        letterSpacing:
                            "1.5px",
                    }}
                >
                    ● ORBITAL INTELLIGENCE ACTIVE
                </div>
            </div>


            {/* BOTTOM LEFT */}

            <div
                style={{
                    position:
                        "absolute",
                    bottom: "30px",
                    left: "32px",
                    fontSize:
                        "8px",
                    color:
                        "#5c7a84",
                    letterSpacing:
                        "1.5px",
                }}
            >
                SATELLITE
                <br />
                ↓
                <br />
                REMOTE SENSING
                <br />
                ↓
                <br />
                GLOF INTELLIGENCE
            </div>


            {/* BOTTOM RIGHT */}

            <div
                style={{
                    position:
                        "absolute",
                    bottom: "30px",
                    right: "32px",
                    textAlign:
                        "right",
                }}
            >
                <div
                    style={{
                        fontSize:
                            "8px",
                        color:
                            "#56747e",
                        letterSpacing:
                            "1.5px",
                    }}
                >
                    TARGET
                </div>

                <div
                    style={{
                        marginTop:
                            "5px",
                        fontSize:
                            "10px",
                        color:
                            "#64e5ff",
                        letterSpacing:
                            "1px",
                    }}
                >
                    HIMALAYAN SECTOR
                </div>
            </div>


            {/* SKIP */}

            {onSkip && (
                <button
                    type="button"
                    onClick={onSkip}
                    style={{
                        position:
                            "absolute",
                        bottom: "28px",
                        left: "50%",
                        transform:
                            "translateX(-50%)",
                        pointerEvents:
                            "auto",
                        padding:
                            "9px 18px",
                        border:
                            "1px solid rgba(83,220,244,.35)",
                        background:
                            "rgba(2,10,16,.7)",
                        color:
                            "#83cbd9",
                        fontSize:
                            "8px",
                        letterSpacing:
                            "1.5px",
                        cursor:
                            "pointer",
                    }}
                >
                    SKIP TO ANALYSIS
                </button>
            )}
        </div>
    );
}


/* ============================================================
   MAIN GLYAB MISSION
============================================================ */

export default function MissionScene({
    onMissionComplete,
}: MissionSceneProps) {
    return (
        <main
            className="mission-scene"
            style={{
                position:
                    "fixed",
                inset: 0,
                overflow:
                    "hidden",
                background:
                    "#010308",
            }}
        >

            <Canvas
                camera={{
                    position: [
                        0,
                        0.4,
                        11,
                    ],
                    fov: 45,
                    near: 0.1,
                    far: 1000,
                }}
                dpr={[
                    1,
                    2,
                ]}
                gl={{
                    antialias: true,
                    powerPreference:
                        "high-performance",
                }}
            >

                {/* BACKGROUND */}

                <color
                    attach="background"
                    args={[
                        "#010308",
                    ]}
                />

                <fog
                    attach="fog"
                    args={[
                        "#010308",
                        18,
                        55,
                    ]}
                />


                {/* LIGHTING */}

                <ambientLight
                    intensity={0.22}
                />

                <directionalLight
                    position={[
                        6,
                        5,
                        8,
                    ]}
                    intensity={3.2}
                />

                <pointLight
                    position={[
                        -6,
                        3,
                        -5,
                    ]}
                    intensity={1.5}
                    color="#38d9ff"
                />

                <pointLight
                    position={[
                        5,
                        -2,
                        4,
                    ]}
                    intensity={0.8}
                    color="#4dffb0"
                />


                {/* SPACE */}

                <StarField />


                {/* ORBIT */}

                <GroundTrack />


                {/* EARTH */}

                <Earth />


                {/* SATELLITE */}

                <OrbitalSatellite />


                {/* SCANNING */}

                <ScanBeam />


                {/* TARGET */}

                <TargetAcquisition />


                {/* CINEMATIC CAMERA */}

                <CameraController
                    onComplete={
                        onMissionComplete
                    }
                />

            </Canvas>


            {/* UI */}

            <MissionHUD
                onSkip={
                    onMissionComplete
                }
            />

        </main>
    );
}