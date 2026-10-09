import { useFrame } from "@react-three/fiber";
import { useRef } from "react";
import * as THREE from "three";

export default function ScanBeam() {
    const beamRef = useRef<THREE.Group>(null);
    const pulseRef = useRef<THREE.Mesh>(null);
    const targetRingRef = useRef<THREE.Mesh>(null);

    const satellitePosition = new THREE.Vector3();
    const targetPosition = new THREE.Vector3(0, 0, 0);

    const direction = new THREE.Vector3();
    const quaternion = new THREE.Quaternion();

    useFrame(({ clock }) => {
        const t = clock.getElapsedTime();

        const radius = 3.8;
        const speed = 0.28;

        satellitePosition.set(
            Math.cos(t * speed) * radius,
            Math.sin(t * speed * 2) * 0.65,
            Math.sin(t * speed) * radius
        );

        direction
            .subVectors(targetPosition, satellitePosition)
            .normalize();

        quaternion.setFromUnitVectors(
            new THREE.Vector3(0, -1, 0),
            direction
        );

        if (beamRef.current) {
            beamRef.current.position.copy(satellitePosition);
            beamRef.current.quaternion.copy(quaternion);
        }

        if (pulseRef.current) {
            const pulse =
                0.65 + Math.sin(t * 5) * 0.25;

            pulseRef.current.scale.set(
                pulse,
                pulse,
                pulse
            );

            const material =
                pulseRef.current.material as THREE.MeshBasicMaterial;

            material.opacity =
                0.35 + Math.sin(t * 5) * 0.15;
        }

        if (targetRingRef.current) {
            targetRingRef.current.rotation.z =
                t * 0.8;

            const scale =
                1 + Math.sin(t * 3) * 0.08;

            targetRingRef.current.scale.set(
                scale,
                scale,
                scale
            );
        }
    });

    return (
        <group>

            {/* Remote sensing beam */}
            <group ref={beamRef}>

                <mesh>
                    <coneGeometry
                        args={[
                            0.30,
                            3.8,
                            48,
                            1,
                            true,
                        ]}
                    />

                    <meshBasicMaterial
                        color="#32d8ff"
                        transparent
                        opacity={0.08}
                        depthWrite={false}
                        side={THREE.DoubleSide}
                        blending={THREE.AdditiveBlending}
                    />
                </mesh>

                {/* Inner scanning cone */}
                <mesh>
                    <coneGeometry
                        args={[
                            0.12,
                            3.8,
                            32,
                            1,
                            true,
                        ]}
                    />

                    <meshBasicMaterial
                        color="#8beaff"
                        transparent
                        opacity={0.10}
                        depthWrite={false}
                        side={THREE.DoubleSide}
                        blending={THREE.AdditiveBlending}
                    />
                </mesh>

                {/* Scanning pulse */}
                <mesh
                    ref={pulseRef}
                    position={[0, -1.8, 0]}
                >
                    <sphereGeometry
                        args={[0.08, 24, 24]}
                    />

                    <meshBasicMaterial
                        color="#9ff3ff"
                        transparent
                        opacity={0.4}
                        depthWrite={false}
                        blending={THREE.AdditiveBlending}
                    />
                </mesh>

            </group>

            {/* Ground acquisition ring */}
            <mesh
                ref={targetRingRef}
                position={[0, -2.48, 0]}
                rotation={[-Math.PI / 2, 0, 0]}
            >
                <ringGeometry args={[0.32, 0.36, 64]} />

                <meshBasicMaterial
                    color="#38e8ff"
                    transparent
                    opacity={0.65}
                    side={THREE.DoubleSide}
                    blending={THREE.AdditiveBlending}
                />
            </mesh>

            {/* Inner acquisition point */}
            <mesh position={[0, -2.47, 0]}>
                <circleGeometry args={[0.06, 32]} />

                <meshBasicMaterial
                    color="#b8f7ff"
                    transparent
                    opacity={0.9}
                    blending={THREE.AdditiveBlending}
                />
            </mesh>

        </group>
    );
}