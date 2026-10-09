import { useState } from "react";

import GlyabLanding from "./components/GlyabLanding";
import MissionScene from "./components/MissionScene";
import RemoteSensingAnalysis from "./components/RemoteSensingAnalysis";
import AIIntelligence from "./components/AIIntelligence";

import "./App.css";

type Screen =
  | "landing"
  | "mission"
  | "remote-sensing"
  | "ai-intelligence";

function App() {
  const [screen, setScreen] = useState<Screen>("landing");

  // ============================================================
  // 01 → 02
  // LANDING → MISSION
  // ============================================================

  const launchMission = () => {
    console.log("GLYAB AI: Mission launched");
    setScreen("mission");
  };

  // ============================================================
  // 02 → 03
  // MISSION → REMOTE SENSING
  // ============================================================

  const missionComplete = () => {
    console.log("GLYAB AI: Mission completed");
    console.log("GLYAB AI: Starting remote sensing analysis");

    setScreen("remote-sensing");
  };

  // ============================================================
  // 03 → 04
  // REMOTE SENSING → AI INTELLIGENCE
  // ============================================================

  const remoteSensingComplete = () => {
    console.log("GLYAB AI: Remote sensing analysis completed");
    console.log("GLYAB AI: Starting AI intelligence engine");

    setScreen("ai-intelligence");
  };

  // ============================================================
  // AI → DIGITAL TWIN
  // ============================================================

  const continueToDigitalTwin = () => {
    console.log("GLYAB AI: Digital Twin ready");

    // Digital Twin screen baad me add karenge.
    // Abhi AI Intelligence screen par hi rahenge.
  };

  // ============================================================
  // APPLICATION
  // ============================================================

  return (
    <main className="app-shell">

      {/* ======================================================
          01 — GLYAB LANDING
          ====================================================== */}

      {screen === "landing" && (
        <GlyabLanding
          onLaunch={launchMission}
        />
      )}

      {/* ======================================================
          02 — CINEMATIC 3D MISSION
          ====================================================== */}

      {screen === "mission" && (
        <MissionScene
          onMissionComplete={missionComplete}
        />
      )}

      {/* ======================================================
          03 — REMOTE SENSING ANALYSIS
          ====================================================== */}

      {screen === "remote-sensing" && (
        <RemoteSensingAnalysis
          onAnalysisComplete={remoteSensingComplete}
        />
      )}

      {/* ======================================================
          04 — AI INTELLIGENCE
          ====================================================== */}

      {screen === "ai-intelligence" && (
        <AIIntelligence
          onContinue={continueToDigitalTwin}
        />
      )}

    </main>
  );
}

export default App;