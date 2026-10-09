import { useMemo, useState } from "react";
import "./AIIntelligence.css";

interface AIIntelligenceProps {
    onContinue?: () => void;
}

type MetricType =
    | "temperature"
    | "water"
    | "glacier";

type ChatMessage = {
    role: "ai" | "user";
    text: string;
};

const temperatureData = [
    1.8,
    2.1,
    2.0,
    2.5,
    2.7,
    3.1,
    2.9,
    3.4,
    3.2,
    3.7,
    3.9,
    4.1,
    4.0,
    4.4,
];

const waterData = [
    42,
    43,
    43,
    45,
    44,
    47,
    49,
    48,
    52,
    54,
    53,
    57,
    59,
    61,
];

const glacierData = [
    100,
    99.8,
    99.6,
    99.4,
    99.1,
    98.9,
    98.6,
    98.2,
    97.9,
    97.5,
    97.1,
    96.7,
    96.1,
    95.5,
];

const shapFeatures = [
    {
        name: "GLACIAL LAKE LEVEL",
        value: 91,
        direction: "RISK ↑",
    },
    {
        name: "TEMPERATURE",
        value: 84,
        direction: "RISK ↑",
    },
    {
        name: "GLACIER MASS",
        value: 72,
        direction: "RISK ↑",
    },
    {
        name: "RAINFALL",
        value: 61,
        direction: "RISK ↑",
    },
    {
        name: "ICE STABILITY",
        value: 48,
        direction: "RISK ↓",
    },
];

const metricInfo = {
    temperature: {
        title: "SURFACE TEMPERATURE",
        value: "4.4",
        unit: "°C",
        change: "+2.6°C",
        label: "24H TREND",
        forecast: "ELEVATED",
        forecastChange: "+12.4%",
        anomaly: "0.81",
        assessment:
            "Increasing thermal signal detected across the observation window.",
        data: temperatureData,
    },

    water: {
        title: "GLACIAL LAKE LEVEL",
        value: "61.0",
        unit: "m",
        change: "+19.0%",
        label: "24H TREND",
        forecast: "RISING",
        forecastChange: "+8.7%",
        anomaly: "0.88",
        assessment:
            "Water-level acceleration indicates elevated hydrological pressure.",
        data: waterData,
    },

    glacier: {
        title: "GLACIER MASS INDEX",
        value: "95.5",
        unit: "%",
        change: "-4.5%",
        label: "OBSERVATION TREND",
        forecast: "DECLINING",
        forecastChange: "-6.2%",
        anomaly: "0.76",
        assessment:
            "Persistent mass-loss signal detected in the current observation window.",
        data: glacierData,
    },
};

function Sparkline({
    values,
}: {
    values: number[];
}) {
    const width = 600;
    const height = 190;

    const min = Math.min(...values);
    const max = Math.max(...values);

    const points = values
        .map((value, index) => {
            const x =
                (index /
                    (values.length - 1)) *
                width;

            const normalized =
                max === min
                    ? 0.5
                    : (value - min) /
                    (max - min);

            const y =
                height -
                normalized *
                (height - 35) -
                18;

            return `${x},${y}`;
        })
        .join(" ");

    return (
        <svg
            className="ai-chart-svg"
            viewBox={`0 0 ${width} ${height}`}
            preserveAspectRatio="none"
        >
            <defs>
                <linearGradient
                    id="aiChartFill"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                >
                    <stop
                        offset="0%"
                        stopColor="#3edfff"
                        stopOpacity=".24"
                    />

                    <stop
                        offset="100%"
                        stopColor="#3edfff"
                        stopOpacity="0"
                    />
                </linearGradient>
            </defs>

            {[0, 1, 2, 3].map(
                (line) => (
                    <line
                        key={line}
                        x1="0"
                        x2={width}
                        y1={
                            35 +
                            line * 40
                        }
                        y2={
                            35 +
                            line * 40
                        }
                        stroke="rgba(78,190,213,.11)"
                        strokeWidth="1"
                    />
                )
            )}

            <polyline
                points={`0,${height} ${points} ${width},${height}`}
                fill="url(#aiChartFill)"
                stroke="none"
            />

            <polyline
                points={points}
                fill="none"
                stroke="#52e5fa"
                strokeWidth="2"
            />

            {values.map(
                (value, index) => {
                    const x =
                        (index /
                            (values.length -
                                1)) *
                        width;

                    const normalized =
                        max === min
                            ? 0.5
                            : (value - min) /
                            (max - min);

                    const y =
                        height -
                        normalized *
                        (height - 35) -
                        18;

                    return (
                        <circle
                            key={`${value}-${index}`}
                            cx={x}
                            cy={y}
                            r="2.5"
                            fill="#78edff"
                        />
                    );
                }
            )}
        </svg>
    );
}

function RiskGauge({
    value,
}: {
    value: number;
}) {
    const radius = 72;
    const circumference =
        2 * Math.PI * radius;

    const progress =
        circumference *
        (value / 100);

    return (
        <div className="risk-gauge">

            <svg
                viewBox="0 0 180 180"
            >
                <circle
                    cx="90"
                    cy="90"
                    r={radius}
                    fill="none"
                    stroke="rgba(57,130,146,.14)"
                    strokeWidth="8"
                />

                <circle
                    cx="90"
                    cy="90"
                    r={radius}
                    fill="none"
                    stroke="#48dff5"
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray={`${progress} ${circumference}`}
                    transform="rotate(-90 90 90)"
                />

                <circle
                    cx="90"
                    cy="90"
                    r="56"
                    fill="rgba(4,20,27,.85)"
                    stroke="rgba(75,205,225,.14)"
                />
            </svg>

            <div className="risk-gauge-center">

                <strong>
                    {value}%
                </strong>

                <span>
                    GLOF RISK
                </span>

            </div>

        </div>
    );
}

function FeatureBar({
    name,
    value,
    direction,
}: {
    name: string;
    value: number;
    direction: string;
}) {
    return (
        <div className="shap-feature">

            <div className="shap-feature-top">

                <span>
                    {name}
                </span>

                <strong>
                    {direction}
                </strong>

            </div>

            <div className="shap-track">

                <div
                    className="shap-fill"
                    style={{
                        width: `${value}%`,
                    }}
                />

            </div>

            <div className="shap-value">
                contribution {value}%
            </div>

        </div>
    );
}

export default function AIIntelligence({
    onContinue,
}: AIIntelligenceProps) {
    const [activeMetric, setActiveMetric] =
        useState<MetricType>(
            "temperature"
        );

    const [riskScore] =
        useState(73);

    const [input, setInput] =
        useState("");

    const [messages, setMessages] =
        useState<ChatMessage[]>([
            {
                role: "ai",
                text:
                    "GLYAB AI Copilot initialized. Remote-sensing features are available for cryosphere risk analysis.",
            },
        ]);

    const [copilotThinking, setCopilotThinking] =
        useState(false);

    const metric =
        metricInfo[activeMetric];

    const riskLevel =
        riskScore >= 70
            ? "HIGH"
            : riskScore >= 40
                ? "MODERATE"
                : "LOW";

    const currentData = useMemo(
        () => metric.data,
        [metric]
    );

    const generateAIResponse = (
        question: string
    ) => {
        const query =
            question.toLowerCase();

        if (
            query.includes("risk") ||
            query.includes("glof") ||
            query.includes("flood")
        ) {
            return "The current prototype risk assessment is elevated. Glacial lake level, temperature and glacier-mass features are the strongest contributors. A production alert must be generated only after the validated backend model evaluates real observations.";
        }

        if (
            query.includes("temperature") ||
            query.includes("heat")
        ) {
            return "The observation window shows an increasing temperature signal. In the production system this feature would be passed to the trained risk model together with lake level, precipitation, glacier mass and terrain variables.";
        }

        if (
            query.includes("water") ||
            query.includes("lake")
        ) {
            return "The monitored lake-level signal is increasing. Rapid water-level change is an important feature for downstream GLOF risk assessment, but the actual alert threshold must come from the validated model and hydrological analysis.";
        }

        if (
            query.includes("glacier") ||
            query.includes("ice")
        ) {
            return "The glacier-mass index shows a declining observation trend in this interface. Production analysis will use actual remote-sensing-derived glacier area, snow/ice indices and temporal change measurements.";
        }

        if (
            query.includes("sensor") ||
            query.includes("esp32") ||
            query.includes("hardware")
        ) {
            return "The GLYAB architecture can ingest field telemetry through an ESP32 gateway using MQTT. Sensor observations can then be synchronized with satellite-derived features before inference.";
        }

        if (
            query.includes("shap") ||
            query.includes("explain")
        ) {
            return "SHAP is used to explain individual model predictions by measuring how each feature contributes to the final risk score. The feature ranking shown here is an interface demonstration until the trained backend model is connected.";
        }

        return "I can analyze GLOF risk, glacier trends, water-level changes, temperature signals, sensor telemetry and model explanations.";
    };

    const sendMessage = (
        text?: string
    ) => {
        const question =
            text ??
            input.trim();

        if (!question) {
            return;
        }

        setMessages(
            (previous) => [
                ...previous,
                {
                    role: "user",
                    text: question,
                },
            ]
        );

        setInput("");

        setCopilotThinking(true);

        window.setTimeout(() => {
            setMessages(
                (previous) => [
                    ...previous,
                    {
                        role: "ai",
                        text:
                            generateAIResponse(
                                question
                            ),
                    },
                ]
            );

            setCopilotThinking(false);
        }, 700);
    };

    return (
        <main className="ai-intelligence">

            {/* =================================================
                HEADER
            ================================================= */}

            <header className="ai-header">

                <div className="ai-brand">

                    <div className="ai-logo">
                        G
                    </div>

                    <div>

                        <div className="ai-brand-name">
                            GLYAB AI
                        </div>

                        <div className="ai-brand-subtitle">
                            CRYOSPHERE INTELLIGENCE ENGINE
                        </div>

                    </div>

                </div>


                <div className="ai-header-center">

                    <div className="ai-live-dot" />

                    AI INTELLIGENCE

                    <span>
                        MODEL ANALYSIS
                    </span>

                </div>


                <div className="ai-header-right">

                    <div>
                        <span>MISSION</span>
                        <strong>RS-001</strong>
                    </div>

                    <div>
                        <span>ENGINE</span>
                        <strong>XGB / SHAP</strong>
                    </div>

                    <div>
                        <span>STATUS</span>
                        <strong>ANALYSIS</strong>
                    </div>

                </div>

            </header>


            {/* =================================================
                TARGET STRIP
            ================================================= */}

            <section className="ai-target-strip">

                <div>
                    <span>TARGET</span>
                    <strong>
                        HIMALAYAN CRYOSPHERE
                    </strong>
                </div>

                <div>
                    <span>LAT</span>
                    <strong>
                        30.421° N
                    </strong>
                </div>

                <div>
                    <span>LON</span>
                    <strong>
                        79.208° E
                    </strong>
                </div>

                <div>
                    <span>ELEVATION</span>
                    <strong>
                        4,870 M
                    </strong>
                </div>

                <div>
                    <span>DATA</span>
                    <strong>
                        SATELLITE + SENSOR
                    </strong>
                </div>

                <div className="validated-state">
                    <i />
                    FEATURES READY
                </div>

            </section>


            {/* =================================================
                MAIN GRID
            ================================================= */}

            <section className="ai-main-grid">

                {/* =============================================
                    LEFT — RISK
                ============================================== */}

                <section className="risk-panel">

                    <div className="section-heading">

                        <div>
                            <span>
                                DECISION INTELLIGENCE
                            </span>

                            <h2>
                                GLOF RISK
                            </h2>
                        </div>

                        <div className="engine-tag">
                            XGBOOST
                        </div>

                    </div>


                    <div className="risk-overview">

                        <RiskGauge
                            value={riskScore}
                        />

                        <div className="risk-summary">

                            <div className="risk-level">
                                {riskLevel}
                            </div>

                            <div className="risk-confidence">

                                <span>
                                    MODEL CONFIDENCE
                                </span>

                                <strong>
                                    91.8%
                                </strong>

                            </div>

                            <div className="risk-state">
                                ELEVATED HYDROLOGICAL
                                CONDITIONS
                            </div>

                        </div>

                    </div>


                    <div className="risk-divider" />


                    <div className="sub-heading">

                        <span>
                            MODEL EXPLAINABILITY
                        </span>

                        <strong>
                            SHAP
                        </strong>

                    </div>

                    <div className="shap-list">

                        {shapFeatures.map(
                            (feature) => (
                                <FeatureBar
                                    key={
                                        feature.name
                                    }
                                    {...feature}
                                />
                            )
                        )}

                    </div>


                    <div className="risk-footnote">

                        <i />

                        Highest contribution:
                        GLACIAL LAKE LEVEL

                    </div>

                </section>


                {/* =============================================
                    CENTER — TIME SERIES
                ============================================== */}

                <section className="trend-panel">

                    <div className="section-heading">

                        <div>
                            <span>
                                ENVIRONMENTAL TELEMETRY
                            </span>

                            <h2>
                                TIME SERIES
                            </h2>
                        </div>

                        <div className="observation-badge">
                            LIVE ANALYSIS
                        </div>

                    </div>


                    <div className="metric-tabs">

                        <button
                            className={
                                activeMetric ===
                                    "temperature"
                                    ? "active"
                                    : ""
                            }
                            onClick={() =>
                                setActiveMetric(
                                    "temperature"
                                )
                            }
                        >
                            TEMPERATURE
                        </button>

                        <button
                            className={
                                activeMetric ===
                                    "water"
                                    ? "active"
                                    : ""
                            }
                            onClick={() =>
                                setActiveMetric(
                                    "water"
                                )
                            }
                        >
                            WATER LEVEL
                        </button>

                        <button
                            className={
                                activeMetric ===
                                    "glacier"
                                    ? "active"
                                    : ""
                            }
                            onClick={() =>
                                setActiveMetric(
                                    "glacier"
                                )
                            }
                        >
                            GLACIER MASS
                        </button>

                    </div>


                    <div className="trend-value-row">

                        <div>

                            <span>
                                {metric.title}
                            </span>

                            <strong>
                                {metric.value}
                                <small>
                                    {metric.unit}
                                </small>
                            </strong>

                        </div>

                        <div className="trend-change">

                            <span>
                                {metric.label}
                            </span>

                            <strong>
                                {metric.change}
                            </strong>

                        </div>

                    </div>


                    <div className="chart-panel">

                        <div className="chart-axis">

                            <span>
                                HIGH
                            </span>

                            <span>
                                MID
                            </span>

                            <span>
                                LOW
                            </span>

                        </div>

                        <Sparkline
                            values={currentData}
                        />

                        <div className="chart-time">

                            <span>
                                -24H
                            </span>

                            <span>
                                -18H
                            </span>

                            <span>
                                -12H
                            </span>

                            <span>
                                -6H
                            </span>

                            <span>
                                NOW
                            </span>

                        </div>

                    </div>


                    <div className="prediction-row">

                        <div className="prediction-card">

                            <span>
                                24H FORECAST
                            </span>

                            <strong>
                                {metric.forecast}
                            </strong>

                            <small>
                                {metric.forecastChange}
                            </small>

                        </div>

                        <div className="prediction-card">

                            <span>
                                ANOMALY SCORE
                            </span>

                            <strong>
                                {metric.anomaly}
                            </strong>

                            <small>
                                ISOLATION FOREST
                            </small>

                        </div>

                        <div className="prediction-card">

                            <span>
                                7D TREND
                            </span>

                            <strong>
                                +12.4%
                            </strong>

                            <small>
                                MODEL PROJECTION
                            </small>

                        </div>

                    </div>


                    <div className="assessment-box">

                        <div className="assessment-icon">
                            AI
                        </div>

                        <div>

                            <span>
                                AI ASSESSMENT
                            </span>

                            <p>
                                {metric.assessment}
                            </p>

                        </div>

                    </div>

                </section>


                {/* =============================================
                    RIGHT — COPILOT
                ============================================== */}

                <section className="copilot-panel">

                    <div className="copilot-header">

                        <div>

                            <span>
                                GLYAB
                            </span>

                            <h2>
                                AI COPILOT
                            </h2>

                        </div>

                        <div className="copilot-status">
                            <i />
                            ONLINE
                        </div>

                    </div>


                    <div className="copilot-description">
                        AI-assisted interpretation
                        of cryosphere observations,
                        predictions and anomalies.
                    </div>


                    <div className="quick-questions">

                        <button
                            onClick={() =>
                                sendMessage(
                                    "What is the current GLOF risk?"
                                )
                            }
                        >
                            GLOF RISK
                        </button>

                        <button
                            onClick={() =>
                                sendMessage(
                                    "Explain the glacier trend."
                                )
                            }
                        >
                            GLACIER TREND
                        </button>

                        <button
                            onClick={() =>
                                sendMessage(
                                    "Why is the risk elevated?"
                                )
                            }
                        >
                            WHY?
                        </button>

                        <button
                            onClick={() =>
                                sendMessage(
                                    "Explain SHAP."
                                )
                            }
                        >
                            EXPLAIN AI
                        </button>

                    </div>


                    <div className="chat-window">

                        {messages.map(
                            (message, index) => (
                                <div
                                    key={`${message.role}-${index}`}
                                    className={
                                        message.role ===
                                            "ai"
                                            ? "chat-message ai"
                                            : "chat-message user"
                                    }
                                >

                                    <div className="chat-avatar">
                                        {message.role ===
                                            "ai"
                                            ? "G"
                                            : "U"}
                                    </div>

                                    <div className="chat-bubble">
                                        {message.text}
                                    </div>

                                </div>
                            )
                        )}

                        {copilotThinking && (
                            <div className="chat-message ai">

                                <div className="chat-avatar">
                                    G
                                </div>

                                <div className="chat-bubble thinking">
                                    <i />
                                    <i />
                                    <i />
                                </div>

                            </div>
                        )}

                    </div>


                    <div className="copilot-input">

                        <input
                            value={input}
                            onChange={(event) =>
                                setInput(
                                    event.target.value
                                )
                            }
                            onKeyDown={(event) => {
                                if (
                                    event.key ===
                                    "Enter"
                                ) {
                                    sendMessage();
                                }
                            }}
                            placeholder="Ask GLYAB AI..."
                        />

                        <button
                            onClick={() =>
                                sendMessage()
                            }
                        >
                            →
                        </button>

                    </div>


                    <div className="copilot-disclaimer">
                        AI COPILOT • MODEL-GROUNDED
                        INTERPRETATION
                    </div>

                </section>

            </section>


            {/* =================================================
                FOOTER
            ================================================= */}

            <footer className="ai-footer">

                <div>
                    <span>
                        REMOTE SENSING
                    </span>
                    <strong>
                        ACQUIRED
                    </strong>
                </div>

                <div>
                    <span>
                        FEATURE ENGINE
                    </span>
                    <strong>
                        READY
                    </strong>
                </div>

                <div>
                    <span>
                        RISK MODEL
                    </span>
                    <strong>
                        XGBOOST
                    </strong>
                </div>

                <div>
                    <span>
                        ANOMALY
                    </span>
                    <strong>
                        ISOLATION FOREST
                    </strong>
                </div>

                <div>
                    <span>
                        EXPLAINABILITY
                    </span>
                    <strong>
                        SHAP
                    </strong>
                </div>

                <div>
                    <span>
                        SENSOR GATEWAY
                    </span>
                    <strong>
                        ESP32 / MQTT
                    </strong>
                </div>

                <button
                    className="digital-twin-button"
                    onClick={() =>
                        onContinue?.()
                    }
                >
                    DIGITAL TWIN →
                </button>

            </footer>

        </main>
    );
}