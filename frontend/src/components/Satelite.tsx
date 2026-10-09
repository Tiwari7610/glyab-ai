import { useFrame } from "@react-three/fiber";
import { useRef } from "react";
import * as THREE from "three";

export default function Satellite() {
    const satelliteRef = useRef<THREE.Group>(null);
    const dishRef = useRef<THREE.Mesh>(null);

    useFrame(({ clock }) => {
        const t = clock.getElapsedTime();

        if (satelliteRef.current) {
            const radius = 3.8;
            const speed = 0.28;

            satelliteRef.current.position.x =
                Math.cos(t * speed) * radius;

            satelliteRef.current.position.z =
                Math.sin(t * speed) * radius;

            satelliteRef.current.position.y =
                Math.sin(t * speed * 2) * 0.65;

            // Satellite points roughly toward Earth
            satelliteRef.current.lookAt(0, 0, 0);
        }

        if (dishRef.current) {
            dishRef.current.rotation.z =
                Math.sin(t * 0.8) * 0.08;
        }
    });

    return (
        <group ref={satelliteRef}>

            {/* Main satellite body */}
            <mesh>
                <boxGeometry args={[0.42, 0.28, 0.65]} />

                <meshStandardMaterial
                    color="#d9e2e7"
                    metalness={0.85}
                    roughness={0.22}
                />
            </mesh>

            {/* Gold thermal panel */}
            <mesh position={[0, 0.01, -0.34]}>
                <boxGeometry args={[0.32, 0.22, 0.035]} />

                <meshStandardMaterial
                    color="#b58b32"
                    metalness={0.65}
                    roughness={0.3}
                />
            </mesh>

            {/* Left solar panel */}
            <mesh position={[-0.75, 0, 0]}>
                <boxGeometry args={[0.9, 0.035, 0.48]} />

                <meshStandardMaterial
                    color="#102e52"
                    metalness={0.75}
                    roughness={0.25}
                />
            </mesh>

            {/* Right solar panel */}
            <mesh position={[0.75, 0, 0]}>
                <boxGeometry args={[0.9, 0.035, 0.48]} />

                <meshStandardMaterial
                    color="#102e52"
                    metalness={0.75}
                    roughness={0.25}
                />
            </mesh>

            {/* Solar panel grid lines */}
            <mesh position={[-0.75, 0.025, 0]}>
                <boxGeometry args={[0.82, 0.008, 0.40]} />

                <meshBasicMaterial color="#3e78a8" />
            </mesh>

            <mesh position={[0.75, 0.025, 0]}>
                <boxGeometry args={[0.82, 0.008, 0.40]} />

                <meshBasicMaterial color="#3e78a8" />
            </mesh>

            {/* Communication antenna arm */}
            <mesh position={[0, -0.38, 0]}>
                <cylinderGeometry args={[0.018, 0.018, 0.45, 16]} />

                <meshStandardMaterial
                    color="#bfc8ce"
                    metalness={0.8}
                    roughness={0.25}
                />
            </mesh>

            {/* Communication dish */}
            <mesh
                ref={dishRef}
                position={[0, -0.62, 0]}
                rotation={[Math.PI, 0, 0]}
            >
                <sphereGeometry
                    args={[0.16, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2]}
                />

                <meshStandardMaterial
                    color="#e5edf2"
                    metalness={0.7}
                    roughness={0.2}
                />
            </mesh>

            {/* Earth observation sensor */}
            <mesh position={[0, 0.18, 0.32]}>
                <cylinderGeometry args={[0.075, 0.075, 0.08, 24]} />

                <meshStandardMaterial
                    color="#111820"
                    metalness={0.4}
                    roughness={0.18}
                />
            </mesh>

            {/* Sensor lens */}
            <mesh position={[0, 0.225, 0.32]}>
                <cylinderGeometry args={[0.045, 0.045, 0.012, 24]} />

                <meshStandardMaterial
                    color="#55cfff"
                    emissive="#087fa8"
                    emissiveIntensity={2}
                    metalness={0.3}
                    roughness={0.12}
                />
            </mesh>

            {/* Small navigation beacon */}
            <mesh position={[0.21, 0.08, 0]}>
                <sphereGeometry args={[0.035, 16, 16]} />

                <meshBasicMaterial color="#59e8b0" />
            </mesh>

        </group>
    );
}