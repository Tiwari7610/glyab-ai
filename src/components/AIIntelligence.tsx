import { useEffect, useState } from "react";

type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

interface GLOFFeatures {
    latitude: number;
    longitude: number;
    area_km2: number;
    elevation_min_m: number;
    elevation_max_m: number;
    mean_elevation_m: number;
    slope_deg: number;
    aspect_deg: number;
    elevation_range_m: number;
    area_log: number;
    o1region: number;
}

interface Prediction {
    prediction: number;
    risk_level: RiskLevel;
    risk_probability: number;
    risk_percentage: number;
}

interface PredictionResponse {
    success: boolean;
    system: string;
    service: string;
    prediction: Prediction;
}

interface ChatMessage {
    role: "user" | "assistant";
    content: string;
}

interface AIIntelligenceProps {
    onContinue: () => void;
}

const API_BASE_URL = "http://127.0.0.1:8000";

const DEFAULT_FEATURES: GLOFFeatures = {
    latitude: 30.63,
    longitude: 79.67,
    area_km2: 0.0619,
    elevation_min_m: 3500,
    elevation_max_m: 5200,
    mean_elevation_m: 4350,
    slope_deg: 18,
    aspect_deg: 180,
    elevation_range_m: 1700,
    area_log: Math.log1p(0.0619),
    o1region: 0,
};

function getRiskClass(level: RiskLevel): string {
    switch (level) {
        case "CRITICAL":
            return "critical";
        case "HIGH":
            return "high";
        case "MEDIUM":
            return "medium";
        default:
            return "low";
    }
}

function AIIntelligence({ onContinue }: AIIntelligenceProps) {
    const [prediction, setPrediction] = useState<Prediction | null>(null);
    const [features, setFeatures] =
        useState<GLOFFeatures>(DEFAULT_FEATURES);

    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string>("");

    const [question, setQuestion] = useState<string>("");
    const [chatLoading, setChatLoading] = useState<boolean>(false);

    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            role: "assistant",
            content:
                "GLYAB AI Copilot is ready. I can explain the current GLOF risk assessment and model inputs.",
        },
    ]);

    const loadPrediction = async () => {
        try {
            setLoading(true);
            setError("");

            const response = await fetch(
                `${API_BASE_URL}/api/v1/glof/predict`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(DEFAULT_FEATURES),
                }
            );

            if (!response.ok) {
                throw new Error(
                    `Prediction API returned ${response.status}`
                );
            }

            const data: PredictionResponse = await response.json();

            if (!data.success || !data.prediction) {
                throw new Error("Invalid prediction response from backend.");
            }

            setPrediction(data.prediction);
            setFeatures(DEFAULT_FEATURES);
        } catch (err) {
            console.error("GLYAB prediction error:", err);

            setError(
                "Unable to connect to GLYAB AI backend. Please make sure FastAPI is running on port 8000."
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadPrediction();
    }, []);

    const sendMessage = async () => {
        const text = question.trim();

        if (!text || chatLoading) {
            return;
        }

        const userMessage: ChatMessage = {
            role: "user",
            content: text,
        };

        setMessages((previous) => [...previous, userMessage]);
        setQuestion("");
        setChatLoading(true);

        try {
            const response = await fetch(
                `${API_BASE_URL}/api/v1/copilot/copilot/chat`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        message: text,
                        context: {
                            risk_level: prediction?.risk_level ?? "UNKNOWN",
                            risk_percentage:
                                prediction?.risk_percentage ?? 0,
                            risk_probability:
                                prediction?.risk_probability ?? 0,
                            model: "GLYAB GLOF Risk Model",
                            features,
                        },
                    }),
                }
            );

            if (!response.ok) {
                throw new Error(
                    `Copilot API returned ${response.status}`
                );
            }

            const data = await response.json();

            const answer =
                data.response ??
                data.message ??
                data.answer ??
                data.reply ??
                "GLYAB Copilot did not return a response.";

            setMessages((previous) => [
                ...previous,
                {
                    role: "assistant",
                    content: String(answer),
                },
            ]);
        } catch (err) {
            console.error("Copilot error:", err);

            setMessages((previous) => [
                ...previous,
                {
                    role: "assistant",
                    content:
                        "Copilot backend is not available right now. Please check the FastAPI server.",
                },
            ]);
        } finally {
            setChatLoading(false);
        }
    };

    const riskLevel: RiskLevel =
        prediction?.risk_level ?? "LOW";

    const riskPercentage = Math.max(
        0,
        Math.min(
            100,
            prediction?.risk_percentage ?? 0
        )
    );

    const riskClass = getRiskClass(riskLevel);

    return (
        <section className="ai-intelligence-page">
            <style>{`
        .ai-intelligence-page {
          min-height: 100vh;
          width: 100%;
          box-sizing: border-box;
          padding: 36px;
          color: #e8f7ff;
          background:
            radial-gradient(circle at top right, rgba(0, 190, 255, 0.12), transparent 35%),
            radial-gradient(circle at bottom left, rgba(0, 120, 255, 0.10), transparent 35%),
            #050b12;
          font-family: Inter, Arial, sans-serif;
        }

        .ai-container {
          max-width: 1400px;
          margin: 0 auto;
        }

        .ai-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 20px;
          margin-bottom: 28px;
        }

        .ai-kicker {
          color: #38d9ff;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 3px;
          margin-bottom: 8px;
        }

        .ai-title {
          margin: 0;
          font-size: 34px;
          font-weight: 800;
        }

        .ai-subtitle {
          margin-top: 8px;
          color: #8ea7b8;
          font-size: 14px;
        }

        .status-pill {
          padding: 9px 14px;
          border: 1px solid rgba(60, 220, 255, 0.35);
          border-radius: 999px;
          background: rgba(0, 180, 255, 0.08);
          color: #55ddff;
          font-size: 12px;
          font-weight: 700;
        }

        .ai-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }

        .panel {
          border: 1px solid rgba(130, 190, 220, 0.15);
          border-radius: 18px;
          background: rgba(10, 22, 32, 0.82);
          box-shadow: 0 18px 60px rgba(0, 0, 0, 0.25);
          padding: 22px;
        }

        .panel-title {
          margin: 0 0 18px;
          font-size: 16px;
          color: #ccefff;
        }

        .risk-card {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 20px;
          padding: 24px;
          border-radius: 16px;
          background: rgba(255, 255, 255, 0.025);
          border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .risk-number {
          font-size: 54px;
          font-weight: 900;
          line-height: 1;
        }

        .risk-label {
          margin-top: 8px;
          font-size: 12px;
          color: #829aaa;
          letter-spacing: 1.5px;
        }

        .risk-badge {
          padding: 10px 16px;
          border-radius: 10px;
          font-size: 13px;
          font-weight: 800;
          letter-spacing: 1px;
        }

        .risk-low {
          color: #57e6a4;
          border-color: rgba(87, 230, 164, 0.35);
          background: rgba(87, 230, 164, 0.08);
        }

        .risk-medium {
          color: #ffd166;
          border-color: rgba(255, 209, 102, 0.35);
          background: rgba(255, 209, 102, 0.08);
        }

        .risk-high {
          color: #ff8a65;
          border-color: rgba(255, 138, 101, 0.35);
          background: rgba(255, 138, 101, 0.08);
        }

        .risk-critical {
          color: #ff5577;
          border-color: rgba(255, 85, 119, 0.35);
          background: rgba(255, 85, 119, 0.08);
        }

        .progress {
          height: 8px;
          margin-top: 20px;
          border-radius: 20px;
          overflow: hidden;
          background: #152531;
        }

        .progress-fill {
          height: 100%;
          border-radius: inherit;
          background: linear-gradient(90deg, #24d8ff, #7b61ff);
          transition: width 0.6s ease;
        }

        .feature-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 10px;
        }

        .feature {
          padding: 12px;
          border-radius: 10px;
          background: rgba(255, 255, 255, 0.025);
          border: 1px solid rgba(255, 255, 255, 0.06);
        }

        .feature-name {
          color: #7590a2;
          font-size: 11px;
          margin-bottom: 5px;
        }

        .feature-value {
          color: #dff7ff;
          font-size: 14px;
          font-weight: 700;
        }

        .chat-panel {
          grid-column: 1 / -1;
        }

        .chat-window {
          height: 300px;
          overflow-y: auto;
          padding: 14px;
          border-radius: 12px;
          background: #03080d;
          border: 1px solid rgba(255, 255, 255, 0.07);
          margin-bottom: 14px;
        }

        .message {
          max-width: 80%;
          padding: 11px 14px;
          margin-bottom: 10px;
          border-radius: 12px;
          font-size: 13px;
          line-height: 1.55;
        }

        .message-user {
          margin-left: auto;
          background: rgba(40, 170, 255, 0.15);
          border: 1px solid rgba(40, 170, 255, 0.25);
        }

        .message-assistant {
          background: rgba(255, 255, 255, 0.045);
          border: 1px solid rgba(255, 255, 255, 0.07);
        }

        .chat-input-row {
          display: flex;
          gap: 10px;
        }

        .chat-input {
          flex: 1;
          min-width: 0;
          padding: 13px 15px;
          border-radius: 10px;
          outline: none;
          border: 1px solid rgba(120, 180, 210, 0.18);
          background: #07121a;
          color: white;
        }

        .button {
          border: none;
          border-radius: 10px;
          padding: 12px 18px;
          cursor: pointer;
          color: white;
          background: linear-gradient(135deg, #087ea4, #5146c7);
          font-weight: 700;
        }

        .button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .error-box {
          margin-top: 15px;
          padding: 12px;
          border-radius: 10px;
          color: #ff9b9b;
          background: rgba(255, 70, 70, 0.08);
          border: 1px solid rgba(255, 70, 70, 0.2);
          font-size: 13px;
        }

        .actions {
          display: flex;
          justify-content: flex-end;
          margin-top: 22px;
        }

        @media (max-width: 850px) {
          .ai-intelligence-page {
            padding: 20px;
          }

          .ai-grid {
            grid-template-columns: 1fr;
          }

          .chat-panel {
            grid-column: auto;
          }

          .ai-header {
            flex-direction: column;
          }
        }
      `}</style>

            <div className="ai-container">
                <header className="ai-header">
                    <div>
                        <div className="ai-kicker">
                            GLYAB AI / INTELLIGENCE ENGINE
                        </div>

                        <h1 className="ai-title">
                            GLOF Risk Intelligence
                        </h1>

                        <div className="ai-subtitle">
                            ML-powered cryosphere hazard assessment
                        </div>
                    </div>

                    <div className="status-pill">
                        {loading ? "MODEL RUNNING" : "MODEL ONLINE"}
                    </div>
                </header>

                <div className="ai-grid">
                    <section className="panel">
                        <h2 className="panel-title">
                            Current Risk Assessment
                        </h2>

                        <div className="risk-card">
                            <div>
                                <div className="risk-number">
                                    {loading
                                        ? "--"
                                        : `${riskPercentage.toFixed(2)}%`}
                                </div>

                                <div className="risk-label">
                                    MODEL RISK PROBABILITY
                                </div>
                            </div>

                            <div
                                className={`risk-badge risk-${getRiskClass(
                                    riskLevel
                                )}`}
                            >
                                {loading ? "ANALYZING" : riskLevel}
                            </div>
                        </div>

                        <div className="progress">
                            <div
                                className="progress-fill"
                                style={{
                                    width: `${riskPercentage}%`,
                                }}
                            />
                        </div>

                        {error && (
                            <div className="error-box">
                                {error}
                            </div>
                        )}
                    </section>

                    <section className="panel">
                        <h2 className="panel-title">
                            Model Input Intelligence
                        </h2>

                        <div className="feature-grid">
                            <div className="feature">
                                <div className="feature-name">
                                    LATITUDE
                                </div>
                                <div className="feature-value">
                                    {features.latitude}
                                </div>
                            </div>

                            <div className="feature">
                                <div className="feature-name">
                                    LONGITUDE
                                </div>
                                <div className="feature-value">
                                    {features.longitude}
                                </div>
                            </div>

                            <div className="feature">
                                <div className="feature-name">
                                    LAKE AREA
                                </div>
                                <div className="feature-value">
                                    {features.area_km2.toFixed(4)} km²
                                </div>
                            </div>

                            <div className="feature">
                                <div className="feature-name">
                                    ELEVATION RANGE
                                </div>
                                <div className="feature-value">
                                    {features.elevation_range_m} m
                                </div>
                            </div>

                            <div className="feature">
                                <div className="feature-name">
                                    MEAN ELEVATION
                                </div>
                                <div className="feature-value">
                                    {features.mean_elevation_m} m
                                </div>
                            </div>

                            <div className="feature">
                                <div className="feature-name">
                                    SLOPE
                                </div>
                                <div className="feature-value">
                                    {features.slope_deg}°
                                </div>
                            </div>

                            <div className="feature">
                                <div className="feature-name">
                                    ASPECT
                                </div>
                                <div className="feature-value">
                                    {features.aspect_deg}°
                                </div>
                            </div>

                            <div className="feature">
                                <div className="feature-name">
                                    PREDICTION
                                </div>
                                <div className="feature-value">
                                    {prediction
                                        ? prediction.prediction
                                        : "--"}
                                </div>
                            </div>
                        </div>
                    </section>

                    <section className="panel chat-panel">
                        <h2 className="panel-title">
                            GLYAB AI Copilot
                        </h2>

                        <div className="chat-window">
                            {messages.map((message, index) => (
                                <div
                                    key={`${message.role}-${index}`}
                                    className={`message ${message.role === "user"
                                        ? "message-user"
                                        : "message-assistant"
                                        }`}
                                >
                                    {message.content}
                                </div>
                            ))}

                            {chatLoading && (
                                <div className="message message-assistant">
                                    GLYAB Copilot is analyzing...
                                </div>
                            )}
                        </div>

                        <div className="chat-input-row">
                            <input
                                className="chat-input"
                                value={question}
                                onChange={(event) =>
                                    setQuestion(event.target.value)
                                }
                                onKeyDown={(event) => {
                                    if (event.key === "Enter") {
                                        sendMessage();
                                    }
                                }}
                                placeholder="Ask GLYAB about the current GLOF risk..."
                            />

                            <button
                                className="button"
                                onClick={sendMessage}
                                disabled={
                                    chatLoading || !question.trim()
                                }
                            >
                                Ask AI
                            </button>
                        </div>
                    </section>
                </div>

                <div className="actions">
                    <button
                        className="button"
                        onClick={onContinue}
                    >
                        Continue to Digital Twin →
                    </button>
                </div>
            </div>
        </section>
    );
}

export default AIIntelligence;