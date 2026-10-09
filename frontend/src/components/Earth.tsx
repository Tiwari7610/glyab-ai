import { useFrame } from "@react-three/fiber";
import { useTexture } from "@react-three/drei";
import { useRef } from "react";
import * as THREE from "three";

export default function Earth() {
    const earthRef = useRef<THREE.Mesh>(null);

    const earthTexture = useTexture("/textures/earth/earth.jpg");

    earthTexture.colorSpace = THREE.SRGBColorSpace;

    useFrame((_, delta) => {
        if (earthRef.current) {
            earthRef.current.rotation.y += delta * 0.035;
        }
    });

    return (
        <group>
            {/* REAL EARTH SURFACE */}
            <mesh ref={earthRef}>
                <sphereGeometry args={[2.5, 192, 192]} />

                <meshStandardMaterial
                    map={earthTexture}
                    roughness={0.72}
                    metalness={0.02}
                />
            </mesh>

            {/* ATMOSPHERIC GLOW */}
            <mesh scale={1.055}>
                <sphereGeometry args={[2.5, 128, 128]} />

                <meshBasicMaterial
                    color="#38bdf8"
                    transparent
                    opacity={0.10}
                    side={THREE.BackSide}
                    depthWrite={false}
                />
            </mesh>
        </group>
    );
}