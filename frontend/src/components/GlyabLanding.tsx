import { useEffect, useMemo, useState } from "react";
import "./GlyabLanding.css";

interface GlyabLandingProps {
    onLaunch: () => void;
}

type Section =
    | "platform"
    | "intelligence"
    | "technology"
    | "mission"
    | "research"
    | "about";

interface SectionInfo {
    label: string;
    title: string;
    description: string;
    modules: string[];
}

const SECTIONS: Record<Section, SectionInfo> = {
    platform: {
        label: "PLATFORM",
        title: "Cryosphere Intelligence Platform",
        description:
            "GLYAB AI connects geographical data, machine learning and intelligent analysis into one extensible cryosphere intelligence platform.",
        modules: [
            "GLOF Risk Assessment",
            "Geographical Feature Analysis",
            "ML Prediction Engine",
            "Dataset Intelligence",
        ],
    },

    intelligence: {
        label: "INTELLIGENCE",
        title: "AI Risk Intelligence",
        description:
            "The current intelligence layer evaluates structured geographical and terrain-related features through the trained GLOF machine-learning model.",
        modules: [
            "11 Model Input Features",
            "GLOF Prediction API",
            "Risk Classification",
            "AI Copilot",
        ],
    },

    technology: {
        label: "TECHNOLOGY",
        title: "Engineering the Intelligence Layer",
        description:
            "A modular React and TypeScript frontend communicates with a Python FastAPI backend and machine-learning services.",
        modules: [
            "React",
            "TypeScript",
            "FastAPI",
            "Python",
            "Pandas",
            "scikit-learn / Joblib",
            "REST API",
        ],
    },

    mission: {
        label: "MISSION",
        title: "From Cryosphere Data to Risk Intelligence",
        description:
            "GLYAB AI focuses on transforming environmental and geographical information into structured GLOF risk intelligence.",
        modules: [
            "Observe",
            "Extract Features",
            "Analyse",
            "Predict",
            "Interpret",
            "Support Decisions",
        ],
    },

    research: {
        label: "RESEARCH",
        title: "Research & Future Intelligence",
        description:
            "The architecture is designed to grow toward remote sensing, automated feature extraction, monitoring, explainability and digital-twin capabilities.",
        modules: [
            "Remote Sensing",
            "Satellite-derived Features",
            "Real-time Monitoring",
            "Explainable AI",
            "Digital Twin",
        ],
    },

    about: {
        label: "ABOUT GLYAB AI",
        title: "Cryosphere Intelligence & GLOF Risk Assessment",
        description:
            "GLYAB AI is an ML-based GLOF risk assessment prototype with an extensible architecture for future cryosphere intelligence capabilities.",
        modules: [
            "React + TypeScript",
            "FastAPI",
            "Trained GLOF Model",
            "Prediction API",
            "Dataset API",
            "AI Copilot",
        ],
    },
};

const PHASES = [
    {
        code: "01",
        name: "DATA INTELLIGENCE",
        text: "Analysing available cryosphere features",
    },
    {
        code: "02",
        name: "TERRAIN ANALYSIS",
        text: "Evaluating geographical feature space",
    },
    {
        code: "03",
        name: "ML RISK ENGINE",
        text: "Running GLOF model intelligence",
    },
    {
        code: "04",
        name: "RISK INTERPRETATION",
        text: "Converting model output into risk intelligence",
    },
    {
        code: "05",
        name: "AI COPILOT",
        text: "Preparing intelligent interpretation",
    },
    {
        code: "06",
        name: "RESEARCH MODE",
        text: "Exploring next-generation capabilities",
    },
];

function GlyabLogo() {
    return (
        <div className="glyab-logo-mark">
            <svg
                viewBox="0 0 120 120"
                xmlns="http://www.w3.org/2000/svg"
                aria-label="GLYAB AI logo"
            >
                <defs>
                    <linearGradient
                        id="glyabGradient"
                        x1="0%"
                        y1="0%"
                        x2="100%"
                        y2="100%"
                    >
                        <stop offset="0%" stopColor="#72edff" />
                        <stop offset="50%" stopColor="#27b9dc" />
                        <stop offset="100%" stopColor="#17627c" />
                    </linearGradient>

                    <filter id="glyabGlow">
                        <feGaussianBlur
                            stdDeviation="2.5"
                            result="blur"
                        />

                        <feMerge>
                            <feMergeNode in="blur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                <ellipse
                    cx="60"
                    cy="60"
                    rx="48"
                    ry="18"
                    fill="none"
                    stroke="url(#glyabGradient)"
                    strokeWidth="2"
                    opacity="0.75"
                    transform="rotate(-28 60 60)"
                />

                <ellipse
                    cx="60"
                    cy="60"
                    rx="48"
                    ry="18"
                    fill="none"
                    stroke="#4edfff"
                    strokeWidth="1"
                    opacity="0.3"
                    transform="rotate(32 60 60)"
                />

                <path
                    d="M28 82 L46 52 L56 67 L68 42 L94 82 Z"
                    fill="none"
                    stroke="url(#glyabGradient)"
                    strokeWidth="4"
                    strokeLinejoin="round"
                    filter="url(#glyabGlow)"
                />

                <path
                    d="M39 78 L51 70 L59 76 L70 65 L84 78"
                    fill="none"
                    stroke="#d9fbff"
                    strokeWidth="2"
                    opacity="0.85"
                />

                <circle
                    cx="68"
                    cy="42"
                    r="5"
                    fill="#8cf3ff"
                    filter="url(#glyabGlow)"
                />

                <circle
                    cx="60"
                    cy="60"
                    r="3"
                    fill="#ffffff"
                />
            </svg>
        </div>
    );
}

function FeatureIcon({
    type,
}: {
    type: "satellite" | "ai" | "hardware";
}) {
    if (type === "satellite") {
        return (
            <svg
                viewBox="0 0 40 40"
                className="feature-icon"
            >
                <rect
                    x="15"
                    y="15"
                    width="10"
                    height="10"
                    rx="1"
                />

                <path d="M11 13 L15 17 L11 21 Z" />
                <path d="M29 19 L25 15 L29 11 Z" />

                <path
                    d="M8 28 Q20 35 32 28"
                    fill="none"
                />
            </svg>
        );
    }

    if (type === "ai") {
        return (
            <svg
                viewBox="0 0 40 40"
                className="feature-icon"
            >
                <rect
                    x="10"
                    y="10"
                    width="20"
                    height="20"
                    rx="4"
                />

                <circle cx="17" cy="18" r="2" />
                <circle cx="23" cy="18" r="2" />

                <path
                    d="M15 24 Q20 28 25 24"
                    fill="none"
                />

                <path d="M20 4 V10" />
                <path d="M20 30 V36" />
                <path d="M4 20 H10" />
                <path d="M30 20 H36" />
            </svg>
        );
    }

    return (
        <svg
            viewBox="0 0 40 40"
            className="feature-icon"
        >
            <rect
                x="11"
                y="8"
                width="18"
                height="24"
                rx="2"
            />

            <circle cx="20" cy="15" r="3" />

            <path d="M15 23 H25" />
            <path d="M15 27 H22" />

            <path d="M7 14 H11" />
            <path d="M7 20 H11" />
            <path d="M29 14 H33" />
            <path d="M29 20 H33" />
        </svg>
    );
}

export default function GlyabLanding({
    onLaunch,
}: GlyabLandingProps) {
    const [activeFeature, setActiveFeature] =
        useState("AI");

    const [activeSection, setActiveSection] =
        useState<Section | null>(null);

    const [searchOpen, setSearchOpen] =
        useState(false);

    const [search, setSearch] =
        useState("");

    const [phaseIndex, setPhaseIndex] =
        useState(0);

    const [seconds, setSeconds] =
        useState(0);

    const [orbitAngle, setOrbitAngle] =
        useState(0);

    /*
     * VISUAL CLOCK
     * Every second the interface moves.
     */
    useEffect(() => {
        const timer = window.setInterval(() => {
            setSeconds((value) => value + 1);
            setOrbitAngle((value) => (value + 7) % 360);
        }, 1000);

        return () => window.clearInterval(timer);
    }, []);

    /*
     * INTELLIGENCE PHASE
     * Every 60 seconds the GLYAB state changes.
     */
    useEffect(() => {
        const phaseTimer = window.setInterval(() => {
            setPhaseIndex(
                (value) => (value + 1) % PHASES.length
            );
        }, 60000);

        return () =>
            window.clearInterval(phaseTimer);
    }, []);

    const phase = PHASES[phaseIndex];

    const filteredSections = useMemo(() => {
        const query = search.trim().toLowerCase();

        if (!query) {
            return Object.entries(SECTIONS) as [
                Section,
                SectionInfo
            ][];
        }

        return (
            Object.entries(SECTIONS) as [
                Section,
                SectionInfo
            ][]
        ).filter(([key, value]) => {
            return (
                key.includes(query) ||
                value.label.toLowerCase().includes(query) ||
                value.title.toLowerCase().includes(query) ||
                value.description
                    .toLowerCase()
                    .includes(query) ||
                value.modules.some((module) =>
                    module
                        .toLowerCase()
                        .includes(query)
                )
            );
        });
    }, [search]);

    const openSection = (section: Section) => {
        setActiveSection(section);
        setSearchOpen(false);
        setSearch("");
    };

    return (
        <main className="glyab-landing">

            {/* BACKGROUND */}

            <div className="landing-glow landing-glow-one" />
            <div className="landing-glow landing-glow-two" />

            <div className="landing-grid" />

            <div className="landing-stars">
                {Array.from({ length: 12 }).map(
                    (_, index) => (
                        <span key={index} />
                    )
                )}
            </div>

            {/* NAVIGATION */}

            <nav className="glyab-nav">

                <button
                    type="button"
                    className="brand-area"
                    onClick={() =>
                        setActiveSection("about")
                    }
                >
                    <GlyabLogo />

                    <div className="brand-text">
                        <strong>GLYAB</strong>
                        <span>AI</span>
                    </div>
                </button>

                <div className="nav-links">

                    <button
                        type="button"
                        onClick={() =>
                            openSection("platform")
                        }
                    >
                        Platform
                    </button>

                    <button
                        type="button"
                        onClick={() =>
                            openSection("intelligence")
                        }
                    >
                        Intelligence
                    </button>

                    <button
                        type="button"
                        onClick={() =>
                            openSection("technology")
                        }
                    >
                        Technology
                    </button>

                    <button
                        type="button"
                        onClick={() =>
                            openSection("mission")
                        }
                    >
                        Mission
                    </button>

                    <button
                        type="button"
                        onClick={() =>
                            openSection("research")
                        }
                    >
                        Research
                    </button>

                </div>

                <div className="nav-actions">

                    <button
                        type="button"
                        className="glyab-search-button"
                        onClick={() =>
                            setSearchOpen(true)
                        }
                        aria-label="Search GLYAB"
                    >
                        ⌕
                    </button>

                    <span className="system-indicator">
                        <i />
                        SYSTEM READY
                    </span>

                    <button
                        type="button"
                        className="nav-launch"
                        onClick={onLaunch}
                    >
                        LAUNCH
                    </button>

                </div>

            </nav>

            {/* HERO */}

            <section className="glyab-hero">

                <div className="hero-content">

                    <div className="hero-kicker">
                        <span className="kicker-line" />

                        <span>
                            CRYOSPHERE INTELLIGENCE PLATFORM
                        </span>

                        <span className="kicker-line" />
                    </div>

                    <h1>
                        GLYAB
                        <span>AI</span>
                    </h1>

                    <h2>
                        Intelligence for a
                        <strong>
                            Changing Cryosphere.
                        </strong>
                    </h2>

                    <p>
                        An ML-based cryosphere intelligence
                        platform focused on GLOF risk
                        assessment, geographical feature
                        analysis and intelligent interpretation.
                    </p>

                    {/* LIVE INTELLIGENCE STRIP */}

                    <div
                        style={{
                            marginTop: "22px",
                            padding: "12px 16px",
                            border:
                                "1px solid rgba(114,237,255,.22)",
                            background:
                                "rgba(4,18,27,.55)",
                            backdropFilter: "blur(12px)",
                            maxWidth: "580px",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            gap: "20px",
                        }}
                    >
                        <div>
                            <small
                                style={{
                                    display: "block",
                                    color: "#5d91a0",
                                    fontSize: "9px",
                                    letterSpacing: "2px",
                                }}
                            >
                                CURRENT INTELLIGENCE PHASE
                            </small>

                            <strong
                                style={{
                                    color: "#8cf3ff",
                                    fontSize: "13px",
                                    letterSpacing: "1.5px",
                                }}
                            >
                                {phase.code} / {phase.name}
                            </strong>

                            <div
                                style={{
                                    color: "#7896a0",
                                    fontSize: "11px",
                                    marginTop: "4px",
                                }}
                            >
                                {phase.text}
                            </div>
                        </div>

                        <div
                            style={{
                                textAlign: "right",
                                minWidth: "75px",
                            }}
                        >
                            <small
                                style={{
                                    display: "block",
                                    color: "#5d91a0",
                                    fontSize: "9px",
                                    letterSpacing: "2px",
                                }}
                            >
                                SYSTEM CLOCK
                            </small>

                            <strong
                                style={{
                                    color: "#d9fbff",
                                    fontSize: "17px",
                                }}
                            >
                                {String(
                                    Math.floor(seconds / 60)
                                ).padStart(2, "0")}
                                :
                                {String(seconds % 60).padStart(
                                    2,
                                    "0"
                                )}
                            </strong>
                        </div>
                    </div>

                    <div className="hero-actions">

                        <button
                            type="button"
                            className="primary-launch"
                            onClick={onLaunch}
                        >
                            <span>
                                LAUNCH GLYAB AI
                            </span>

                            <b>→</b>
                        </button>

                        <button
                            type="button"
                            className="secondary-button"
                            onClick={() =>
                                openSection("mission")
                            }
                        >
                            EXPLORE MISSION
                        </button>

                    </div>

                    <div className="hero-meta">

                        <div>
                            <strong>01</strong>
                            <span>
                                GLOF
                                <br />
                                ANALYSIS
                            </span>
                        </div>

                        <div>
                            <strong>02</strong>
                            <span>
                                AI RISK
                                <br />
                                PREDICTION
                            </span>
                        </div>

                        <div>
                            <strong>03</strong>
                            <span>
                                DATA
                                <br />
                                INTELLIGENCE
                            </span>
                        </div>

                        <div>
                            <strong>04</strong>
                            <span>
                                FUTURE
                                <br />
                                DIGITAL TWIN
                            </span>
                        </div>

                    </div>

                </div>

                {/* ORBITAL VISUAL */}

                <div className="hero-visual">

                    <div
                        className="orbital-system"
                        style={{
                            transform: `rotate(${orbitAngle}deg)`,
                            transition:
                                "transform .95s linear",
                        }}
                    >

                        <div className="orbit orbit-a" />
                        <div className="orbit orbit-b" />
                        <div className="orbit orbit-c" />

                        <div
                            className="planet-core"
                            style={{
                                transform: `rotate(${-orbitAngle}deg)`,
                            }}
                        >
                            <div className="core-glow" />

                            <GlyabLogo />

                            <div className="core-label">
                                GLYAB AI
                            </div>
                        </div>

                        <div className="orbit-node node-one">
                            RS
                        </div>

                        <div className="orbit-node node-two">
                            AI
                        </div>

                        <div className="orbit-node node-three">
                            ML
                        </div>

                        <div className="orbit-node node-four">
                            DT
                        </div>

                    </div>

                    <div className="visual-data visual-data-top">
                        <span>
                            {phase.name}
                        </span>

                        <strong>
                            {phase.code} / 06
                        </strong>
                    </div>

                    <div className="visual-data visual-data-bottom">
                        <span>
                            EARTH SYSTEM
                        </span>

                        <span>
                            GLYAB / AI / GLOF
                        </span>
                    </div>

                </div>

            </section>

            {/* CAPABILITIES */}

            <section className="capabilities">

                <div className="capability-heading">
                    <span>
                        GLYAB INTELLIGENCE
                    </span>

                    <h3>
                        One system.
                        <strong>
                            Multiple layers of intelligence.
                        </strong>
                    </h3>
                </div>

                <div className="capability-cards">

                    <button
                        type="button"
                        className={
                            activeFeature === "REMOTE"
                                ? "capability-card active"
                                : "capability-card"
                        }
                        onMouseEnter={() =>
                            setActiveFeature("REMOTE")
                        }
                        onClick={() =>
                            openSection("research")
                        }
                    >
                        <FeatureIcon type="satellite" />

                        <span>
                            REMOTE SENSING
                        </span>

                        <strong>
                            Satellite →
                            Glacier
                        </strong>

                        <small>
                            Future research integration
                            for satellite-derived
                            cryosphere intelligence.
                        </small>
                    </button>

                    <button
                        type="button"
                        className={
                            activeFeature === "AI"
                                ? "capability-card active"
                                : "capability-card"
                        }
                        onMouseEnter={() =>
                            setActiveFeature("AI")
                        }
                        onClick={() =>
                            openSection("intelligence")
                        }
                    >
                        <FeatureIcon type="ai" />

                        <span>
                            AI ENGINE
                        </span>

                        <strong>
                            Predict →
                            Interpret
                        </strong>

                        <small>
                            ML-based GLOF risk
                            assessment and
                            intelligent interpretation.
                        </small>
                    </button>

                    <button
                        type="button"
                        className={
                            activeFeature === "HARDWARE"
                                ? "capability-card active"
                                : "capability-card"
                        }
                        onMouseEnter={() =>
                            setActiveFeature("HARDWARE")
                        }
                        onClick={() =>
                            openSection("technology")
                        }
                    >
                        <FeatureIcon type="hardware" />

                        <span>
                            SYSTEM LINK
                        </span>

                        <strong>
                            Data →
                            Intelligence
                        </strong>

                        <small>
                            Extensible architecture
                            for future sensing and
                            monitoring systems.
                        </small>
                    </button>

                </div>

            </section>

            {/* FOOTER */}

            <footer className="glyab-footer">

                <div>
                    GLYAB AI
                </div>

                <div>
                    CRYOSPHERE INTELLIGENCE /
                    RESEARCH PROTOTYPE
                </div>

                <div>
                    ML + DATA + AI
                </div>

            </footer>

            {/* SEARCH OVERLAY */}

            {searchOpen && (
                <div
                    style={{
                        position: "fixed",
                        inset: 0,
                        zIndex: 9999,
                        background:
                            "rgba(1,7,11,.88)",
                        backdropFilter: "blur(18px)",
                        display: "flex",
                        alignItems: "flex-start",
                        justifyContent: "center",
                        paddingTop: "12vh",
                    }}
                    onClick={() =>
                        setSearchOpen(false)
                    }
                >
                    <div
                        style={{
                            width: "min(720px, 92vw)",
                            border:
                                "1px solid rgba(114,237,255,.3)",
                            background:
                                "linear-gradient(145deg,rgba(7,23,33,.98),rgba(2,9,14,.98))",
                            boxShadow:
                                "0 0 80px rgba(39,185,220,.12)",
                            padding: "28px",
                        }}
                        onClick={(event) =>
                            event.stopPropagation()
                        }
                    >
                        <div
                            style={{
                                display: "flex",
                                justifyContent:
                                    "space-between",
                                alignItems: "center",
                                marginBottom: "20px",
                            }}
                        >
                            <div>
                                <small
                                    style={{
                                        color: "#5d91a0",
                                        letterSpacing: "3px",
                                    }}
                                >
                                    GLYAB INTELLIGENCE
                                </small>

                                <h2
                                    style={{
                                        margin:
                                            "5px 0 0",
                                        color: "#d9fbff",
                                    }}
                                >
                                    SEARCH SYSTEM
                                </h2>
                            </div>

                            <button
                                type="button"
                                onClick={() =>
                                    setSearchOpen(false)
                                }
                                style={{
                                    background: "none",
                                    border: 0,
                                    color: "#72edff",
                                    fontSize: "25px",
                                    cursor: "pointer",
                                }}
                            >
                                ×
                            </button>
                        </div>

                        <input
                            autoFocus
                            value={search}
                            onChange={(event) =>
                                setSearch(
                                    event.target.value
                                )
                            }
                            placeholder="Search glacier, GLOF, AI, research..."
                            style={{
                                width: "100%",
                                boxSizing: "border-box",
                                padding:
                                    "15px 16px",
                                background:
                                    "rgba(0,0,0,.35)",
                                border:
                                    "1px solid rgba(114,237,255,.2)",
                                outline: "none",
                                color: "#d9fbff",
                                fontSize: "14px",
                            }}
                        />

                        <div
                            style={{
                                marginTop: "18px",
                                display: "grid",
                                gap: "8px",
                            }}
                        >
                            {filteredSections.length ===
                                0 ? (
                                <div
                                    style={{
                                        padding: "25px",
                                        color: "#75929d",
                                        textAlign: "center",
                                    }}
                                >
                                    NO GLYAB INTELLIGENCE
                                    MATCH FOUND
                                </div>
                            ) : (
                                filteredSections.map(
                                    ([key, value]) => (
                                        <button
                                            type="button"
                                            key={key}
                                            onClick={() =>
                                                openSection(
                                                    key
                                                )
                                            }
                                            style={{
                                                textAlign:
                                                    "left",
                                                padding:
                                                    "15px",
                                                background:
                                                    "rgba(114,237,255,.035)",
                                                border:
                                                    "1px solid rgba(114,237,255,.1)",
                                                color:
                                                    "#d9fbff",
                                                cursor:
                                                    "pointer",
                                            }}
                                        >
                                            <small
                                                style={{
                                                    color:
                                                        "#5fcde7",
                                                    letterSpacing:
                                                        "2px",
                                                }}
                                            >
                                                {
                                                    value.label
                                                }
                                            </small>

                                            <strong
                                                style={{
                                                    display:
                                                        "block",
                                                    marginTop:
                                                        "4px",
                                                }}
                                            >
                                                {
                                                    value.title
                                                }
                                            </strong>
                                        </button>
                                    )
                                )
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* INFORMATION OVERLAY */}

            {activeSection && (
                <div
                    style={{
                        position: "fixed",
                        inset: 0,
                        zIndex: 10000,
                        background:
                            "rgba(1,7,11,.9)",
                        backdropFilter: "blur(16px)",
                        overflowY: "auto",
                        padding: "7vh 20px",
                    }}
                    onClick={() =>
                        setActiveSection(null)
                    }
                >
                    <div
                        style={{
                            maxWidth: "1050px",
                            margin: "auto",
                            border:
                                "1px solid rgba(114,237,255,.25)",
                            background:
                                "linear-gradient(145deg,#071821,#02090e)",
                            padding:
                                "clamp(25px,5vw,55px)",
                            boxShadow:
                                "0 0 100px rgba(39,185,220,.08)",
                        }}
                        onClick={(event) =>
                            event.stopPropagation()
                        }
                    >
                        <div
                            style={{
                                display: "flex",
                                justifyContent:
                                    "space-between",
                                alignItems: "flex-start",
                            }}
                        >
                            <div>
                                <small
                                    style={{
                                        color:
                                            "#72edff",
                                        letterSpacing:
                                            "3px",
                                    }}
                                >
                                    {
                                        SECTIONS[
                                            activeSection
                                        ].label
                                    }
                                </small>

                                <h1
                                    style={{
                                        color:
                                            "#d9fbff",
                                        fontSize:
                                            "clamp(28px,5vw,55px)",
                                        margin:
                                            "12px 0",
                                    }}
                                >
                                    {
                                        SECTIONS[
                                            activeSection
                                        ].title
                                    }
                                </h1>
                            </div>

                            <button
                                type="button"
                                onClick={() =>
                                    setActiveSection(
                                        null
                                    )
                                }
                                style={{
                                    background: "none",
                                    border: 0,
                                    color:
                                        "#72edff",
                                    fontSize:
                                        "30px",
                                    cursor:
                                        "pointer",
                                }}
                            >
                                ×
                            </button>
                        </div>

                        <p
                            style={{
                                color: "#91adb6",
                                fontSize: "16px",
                                lineHeight: 1.8,
                                maxWidth: "800px",
                            }}
                        >
                            {
                                SECTIONS[
                                    activeSection
                                ].description
                            }
                        </p>

                        <div
                            style={{
                                marginTop: "35px",
                                display: "grid",
                                gridTemplateColumns:
                                    "repeat(auto-fit,minmax(190px,1fr))",
                                gap: "10px",
                            }}
                        >
                            {SECTIONS[
                                activeSection
                            ].modules.map(
                                (module, index) => (
                                    <div
                                        key={module}
                                        style={{
                                            padding:
                                                "18px",
                                            border:
                                                "1px solid rgba(114,237,255,.12)",
                                            background:
                                                "rgba(114,237,255,.025)",
                                        }}
                                    >
                                        <small
                                            style={{
                                                color:
                                                    "#4d7d89",
                                            }}
                                        >
                                            {String(
                                                index + 1
                                            ).padStart(
                                                2,
                                                "0"
                                            )}
                                        </small>

                                        <strong
                                            style={{
                                                display:
                                                    "block",
                                                color:
                                                    "#c9f8ff",
                                                marginTop:
                                                    "8px",
                                            }}
                                        >
                                            {module}
                                        </strong>
                                    </div>
                                )
                            )}
                        </div>

                        <div
                            style={{
                                marginTop: "35px",
                                padding:
                                    "15px 18px",
                                borderTop:
                                    "1px solid rgba(114,237,255,.12)",
                                color: "#5d91a0",
                                fontSize: "11px",
                                letterSpacing: "2px",
                            }}
                        >
                            GLYAB AI / INTELLIGENCE
                            DOSSIER / SYSTEM ONLINE
                        </div>
                    </div>
                </div>
            )}

        </main>
    );
}