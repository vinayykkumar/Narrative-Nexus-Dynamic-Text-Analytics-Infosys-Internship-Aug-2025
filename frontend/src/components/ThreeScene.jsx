import React from "react";
import { Canvas } from "@react-three/fiber";
import { Float, MeshDistortMaterial } from "@react-three/drei";
export default function ThreeScene() {
  return (
    <div className="absolute inset-0 w-full h-full z-20 pointer-events-none">
      <Canvas camera={{ position: [0, 0, 8.5] }}>
        <ambientLight intensity={0.7} />
        <Float speed={2} rotationIntensity={1.2} floatIntensity={0.8}>
          <mesh visible position={[0, 0, 0]}>
            <icosahedronGeometry args={[2.3, 2]} />
            <MeshDistortMaterial color="#00fff7" distort={0.31} speed={1.2} roughness={0.39} />
          </mesh>
        </Float>
      </Canvas>
    </div>
  );
}
