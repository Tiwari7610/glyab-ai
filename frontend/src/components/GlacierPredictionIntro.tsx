import { Canvas, useFrame } from "@react-three/fiber";
import { Html, OrbitControls, Stars } from "@react-three/drei";
import { useRef, useState } from "react";
import * as THREE from "three";
import "./GlacierPredictionIntro.css";

/* =========================================================
   TYPES
========================================================= */

interface GlacierPredictionIntroProps {
    onEnter?: () => void;
}

/* =========================================================
   PLANET DATA
========================================================= */

const planets = [
    {
        name: "MERCURY",
        radius: 0.12,
        orbit: 2.0,
        speed: 1.65,
        size: 0.14,
        color: "#8c8c8c",
    },
    {
        name: "VENUS",
        radius: 0.17,
        orbit: 2.8,
        speed: 1.15,
        size: 0.20,
        color: "#d5a86e",
    },
    {
        name: "EARTH",
        radius: 0.21,
        orbit: 3.7,
        speed: 0.82,
        size: 0.24,
        color: "#268cff",
    },
    {
        name: "MARS",
        radius: 0.16,
        orbit: 4.6,
        speed: 0.63,
        size: 0.18,
        color: "#c95d3d",
    },
    {
        name: "JUPITER",
        radius: 0.42,
        orbit: 5.8,
        speed: 0.35,
        size: 0.43,
        color: "#c99a70",
    },
    {
        name: "SATURN",
        radius: 0.34,
        orbit: 7.0,
        speed: 0.25,
        size: 0.35,
        color: "#d7bd82",
    },
];

/* =========================================================
   ORBIT RING
========================================================= */

function OrbitRing({
    radius,
    rotation = [0, 0, 0],
}: {
    radius: number;
    rotation?: [number, number, number];
}) {
    return (
        <mesh rotation={rotation}>
            <torusGeometry args={[radius, 0.006, 8, 160]} />

            <meshBasicMaterial
                color="#177d9b"
                transparent
                opacity={0.24}
            />
        </mesh>
    );
}

/* =========================================================
   SUN
========================================================= */

function Sun() {
    const sunRef = useRef<THREE.Mesh>(null);

    useFrame((_, delta) => {
        if (sunRef.current) {
            sunRef.current.rotation.y += delta * 0.15;
        }
    });

    return (
        <group>
            {/* Outer glow */}

            <mesh scale={1.35}>
                <sphereGeometry args={[0.72, 48, 48]} />

                <meshBasicMaterial
                    color="#ffb52e"
                    transparent
                    opacity={0.07}
                />
            </mesh>

            {/* Main Sun */}

            <mesh ref={sunRef}>
                <sphereGeometry args={[0.72, 64, 64]} />

                <meshStandardMaterial
                    color="#ffb52e"
                    emissive="#ff7a00"
                    emissiveIntensity={3}
                    roughness={0.8}
                />
            </mesh>

            {/* Sun light */}

            <pointLight
                color="#ffd27a"
                intensity={14}
                distance={30}
            />
        </group>
    );
}

/* =========================================================
   PLANET
========================================================= */

function Planet({
    planet,
    selected,
    onSelect,
}: {
    planet: (typeof planets)[number];
    selected: boolean;
    onSelect: () => void;
}) {
    const groupRef = useRef<THREE.Group>(null);
    const planetRef = useRef<THREE.Mesh>(null);

    useFrame(({ clock }) => {
        if (!groupRef.current) {
            return;
        }

        const time = clock.getElapsedTime();

        const angle =
            time * planet.speed * 0.22 +
            planet.orbit;

        groupRef.current.position.x =
            Math.cos(angle) * planet.orbit;

        groupRef.current.position.z =
            Math.sin(angle) * planet.orbit;

        groupRef.current.position.y =
            Math.sin(angle * 1.7) *
            0.10;

        if (planetRef.current) {
            planetRef.current.rotation.y +=
                0.008;
        }
    });

    const isEarth = planet.name === "EARTH";

    return (
        <group ref={groupRef}>
            {/* Earth selection field */}

            {isEarth && (
                <>
                    <mesh scale={selected ? 1.7 : 1.25}>
                        <sphereGeometry
                            args={[planet.size, 32, 32]}
                        />

                        <meshBasicMaterial
                            color="#27dfff"
                            transparent
                            opacity={selected ? 0.14 : 0.045}
                            depthWrite={false}
                        />
                    </mesh>

                    <mesh
                        rotation={[Math.PI / 2, 0, 0]}
                        onClick={(event) => {
                            event.stopPropagation();
                            onSelect();
                        }}
                    >
                        <torusGeometry
                            args={[
                                selected
                                    ? planet.size * 1.55
                                    : planet.size * 1.30,
                                0.012,
                                12,
                                64,
                            ]}
                        />

                        <meshBasicMaterial
                            color="#39eaff"
                            transparent
                            opacity={
                                selected ? 0.9 : 0.5
                            }
                        />
                    </mesh>
                </>
            )}

            {/* Planet */}

            <mesh
                ref={planetRef}
                onClick={(event) => {
                    event.stopPropagation();

                    if (isEarth) {
                        onSelect();
                    }
                }}
            >
                <sphereGeometry
                    args={[
                        planet.size,
                        32,
                        32,
                    ]}
                />

                <meshStandardMaterial
                    color={planet.color}
                    emissive={
                        isEarth
                            ? "#006dff"
                            : "#000000"
                    }
                    emissiveIntensity={
                        isEarth ? 0.8 : 0
                    }
                    roughness={0.72}
                />
            </mesh>

            {/* Saturn rings */}

            {planet.name === "SATURN" && (
                <mesh
                    rotation={[
                        Math.PI / 2.8,
                        0.2,
                        0,
                    ]}
                >
                    <torusGeometry
                        args={[
                            planet.size * 1.55,
                            0.045,
                            8,
                            64,
                        ]}
                    />

                    <meshStandardMaterial
                        color="#b9a56f"
                        transparent
                        opacity={0.75}
                    />
                </mesh>
            )}

            {/* Earth label */}

            {isEarth && selected && (
                <Html
                    position={[
                        0.35,
                        0.38,
                        0,
                    ]}
                    distanceFactor={8}
                >
                    <div className="earth-lock-label">
                        <span>● TARGET SELECTED</span>
                        <strong>EARTH</strong>
                        <small>
                            CRYOSPHERE ANALYSIS TARGET
                        </small>
                    </div>
                </Html>
            )}
        </group>
    );
}

/* =========================================================
   CAMERA / MISSION CONTROLLER
========================================================= */

function MissionCamera({
    earthSelected,
}: {
    earthSelected: boolean;
}) {
    const progressRef =
        useRef(0);

    useFrame(({ camera }, delta) => {
        if (!earthSelected) {
            progressRef.current = Math.max(
                0,
                progressRef.current -
                delta * 0.15
            );

            const orbit =
                10.8 +
                Math.sin(
                    progressRef.current
                ) * 0.5;

            camera.position.lerp(
                new THREE.Vector3(
                    0,
                    5.5,
                    orbit
                ),
                0.025
            );

            camera.lookAt(0, 0, 0);

            return;
        }

        progressRef.current =
            Math.min(
                1,
                progressRef.current +
                delta * 0.16
            );

        const p =
            progressRef.current;

        const eased =
            1 -
            Math.pow(1 - p, 3);

        const start =
            new THREE.Vector3(
                0,
                5.5,
                10.8
            );

        const end =
            new THREE.Vector3(
                0,
                1.8,
                4.4
            );

        camera.position.lerpVectors(
            start,
            end,
            eased
        );

        camera.lookAt(
            0,
            0,
            0
        );
    });

    return null;
}

/* =========================================================
   SOLAR SYSTEM
========================================================= */

function SolarSystem({
    earthSelected,
    onEarthSelect,
}: {
    earthSelected: boolean;
    onEarthSelect: () => void;
}) {
    return (
        <group>
            {/* Sun */}

            <Sun />

            {/* Orbital architecture */}

            <OrbitRing radius={2.0} />

            <OrbitRing
                radius={2.8}
                rotation={[
                    0.05,
                    0.2,
                    0.08,
                ]}
            />

            <OrbitRing
                radius={3.7}
                rotation={[
                    0.08,
                    -0.18,
                    0.04,
                ]}
            />

            <OrbitRing
                radius={4.6}
                rotation={[
                    -0.06,
                    0.14,
                    0.12,
                ]}
            />

            <OrbitRing
                radius={5.8}
                rotation={[
                    0.11,
                    -0.08,
                    -0.08,
                ]}
            />

            <OrbitRing
                radius={7.0}
                rotation={[
                    -0.12,
                    0.16,
                    0.04,
                ]}
            />

            {/* Planets */}

            {planets.map((planet) => (
                <Planet
                    key={planet.name}
                    planet={planet}
                    selected={
                        earthSelected &&
                        planet.name === "EARTH"
                    }
                    onSelect={onEarthSelect}
                />
            ))}
        </group>
    );
}

/* =========================================================
   MAIN COMPONENT
========================================================= */

export default function GlacierPredictionIntro({
    onEnter,
}: GlacierPredictionIntroProps) {
    const [earthSelected, setEarthSelected] =
        useState(false);

    return (
        <div className="glacier-intro">

            {/* ==================================================
          3D CANVAS
      ================================================== */}

            <Canvas
                camera={{
                    position: [
                        0,
                        5.5,
                        10.8,
                    ],
                    fov: 42,
                    near: 0.1,
                    far: 100,
                }}
                dpr={[1, 2]}
                gl={{
                    antialias: true,
                    powerPreference:
                        "high-performance",
                }}
            >
                {/* Deep space */}

                <color
                    attach="background"
                    args={["#01060b"]}
                />

                {/* Stars */}

                <Stars
                    radius={55}
                    depth={35}
                    count={4500}
                    factor={3}
                    saturation={0}
                    fade
                    speed={0.35}
                />

                {/* Lighting */}

                <ambientLight intensity={0.12} />

                <directionalLight
                    position={[
                        5,
                        6,
                        8,
                    ]}
                    intensity={1.3}
                />

                {/* Solar system */}

                <SolarSystem
                    earthSelected={
                        earthSelected
                    }
                    onEarthSelect={() =>
                        setEarthSelected(true)
                    }
                />

                {/* Camera */}

                <MissionCamera
                    earthSelected={
                        earthSelected
                    }
                />

                {/* User can inspect system */}

                <OrbitControls
                    enablePan={false}
                    enableZoom={!earthSelected}
                    minDistance={7}
                    maxDistance={18}
                    autoRotate={!earthSelected}
                    autoRotateSpeed={0.18}
                    maxPolarAngle={
                        Math.PI * 0.82
                    }
                    minPolarAngle={
                        Math.PI * 0.22
                    }
                />
            </Canvas>

            {/* ==================================================
          TOP MISSION HUD
      ================================================== */}

            <div className="glacier-hud-top">

                <div className="glyab-brand">
                    <div className="glyab-logo">
                        G
                    </div>

                    <div>
                        <strong>
                            GLYAB AI
                        </strong>

                        <span>
                            CRYOSPHERE INTELLIGENCE
                        </span>
                    </div>
                </div>

                <div className="mission-status">
                    <span className="status-dot" />
                    MISSION INITIALIZATION
                </div>

            </div>

            {/* ==================================================
          LEFT INFORMATION
      ================================================== */}

            <div className="glacier-left-panel">

                <div className="eyebrow">
                    GLYAB / MISSION 01
                </div>

                <h1>
                    GLACIER
                    <br />
                    <span>PREDICTION</span>
                </h1>

                <p>
                    AI-powered cryosphere
                    intelligence system for
                    glacier monitoring,
                    change detection and
                    GLOF risk analysis.
                </p>

                <div className="system-line">
                    <span />
                    REMOTE SENSING
                    INTELLIGENCE
                </div>

            </div>

            {/* ==================================================
          EARTH TARGET MESSAGE
      ================================================== */}

            {!earthSelected && (
                <div className="earth-instruction">
                    <span>
                        SELECT EARTH
                    </span>

                    <small>
                        CLICK THE BLUE PLANET
                        TO INITIALIZE CRYOSPHERE
                        MISSION
                    </small>
                </div>
            )}

            {/* ==================================================
          EARTH SELECTED
      ================================================== */}

            {earthSelected && (
                <div className="target-confirmation">

                    <div className="target-icon">
                        ◉
                    </div>

                    <div>
                        <span>
                            PLANETARY TARGET
                        </span>

                        <strong>
                            EARTH ACQUIRED
                        </strong>

                        <small>
                            INITIALIZING GLACIER
                            OBSERVATION PROTOCOL
                        </small>
                    </div>

                </div>
            )}

            {/* ==================================================
          ENTER MISSION
      ================================================== */}

            {earthSelected && (
                <button
                    className="mission-enter-button"
                    onClick={() => {
                        onEnter?.();
                    }}
                >
                    <span>
                        ENTER GLACIER MISSION
                    </span>

                    <b>
                        →
                    </b>
                </button>
            )}

            {/* ==================================================
          BOTTOM TELEMETRY
      ================================================== */}

            <div className="glacier-bottom-bar">

                <div>
                    <span>
                        SYSTEM
                    </span>

                    <strong>
                        GLYAB-CRYO-01
                    </strong>
                </div>

                <div>
                    <span>
                        TARGET
                    </span>

                    <strong>
                        EARTH
                    </strong>
                </div>

                <div>
                    <span>
                        MODE
                    </span>

                    <strong>
                        REMOTE SENSING
                    </strong>
                </div>

                <div>
                    <span>
                        AI STATUS
                    </span>

                    <strong className="ready">
                        STANDBY
                    </strong>
                </div>

            </div>

        </div>
    );
}