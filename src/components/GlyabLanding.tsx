import React from "react";

interface GlyabLandingProps {
    onLaunch: () => void;
}

const GlyabLanding: React.FC<GlyabLandingProps> = ({ onLaunch }) => {
    return (
        <div style={styles.page}>
            {/* Background */}
            <div style={styles.glowOne}></div>
            <div style={styles.glowTwo}></div>

            {/* Navigation */}
            <nav style={styles.navbar}>
                <div style={styles.logoBox}>
                    <div style={styles.logoMark}>G</div>

                    <div>
                        <div style={styles.logoText}>GLYAB AI</div>
                        <div style={styles.logoSub}>CRYOSPHERE INTELLIGENCE</div>
                    </div>
                </div>

                <div style={styles.status}>
                    <span style={styles.statusDot}></span>
                    SYSTEM ONLINE
                </div>
            </nav>

            {/* Hero */}
            <section style={styles.hero}>
                <div style={styles.badge}>
                    <span>◈</span>
                    AI-POWERED GLACIAL RISK INTELLIGENCE
                </div>

                <h1 style={styles.title}>
                    Understanding the
                    <br />
                    <span style={styles.gradientText}>Cryosphere.</span>
                </h1>

                <p style={styles.description}>
                    GLYAB AI is an intelligent GLOF risk assessment platform designed
                    to analyse cryosphere, terrain and geographical information using
                    machine learning.
                </p>

                <p style={styles.subDescription}>
                    From geographical features to AI-driven risk intelligence —
                    GLYAB connects data, machine learning and future remote-sensing
                    capabilities into one unified system.
                </p>

                {/* CTA */}
                <div style={styles.actions}>
                    <button style={styles.primaryButton} onClick={onLaunch}>
                        <span>LAUNCH MISSION</span>
                        <span style={styles.arrow}>→</span>
                    </button>

                    <div style={styles.liveIndicator}>
                        <span style={styles.liveDot}></span>
                        ML ENGINE READY
                    </div>
                </div>
            </section>

            {/* Intelligence Cards */}
            <section style={styles.cardsSection}>
                <div style={styles.card}>
                    <div style={styles.cardIcon}>❄</div>
                    <div>
                        <h3 style={styles.cardTitle}>CRYOSPHERE</h3>
                        <p style={styles.cardText}>
                            Glacier and glacial-lake focused environmental intelligence.
                        </p>
                    </div>
                </div>

                <div style={styles.card}>
                    <div style={styles.cardIcon}>◉</div>
                    <div>
                        <h3 style={styles.cardTitle}>GLOF RISK</h3>
                        <p style={styles.cardText}>
                            Machine-learning based assessment of potential GLOF risk.
                        </p>
                    </div>
                </div>

                <div style={styles.card}>
                    <div style={styles.cardIcon}>⌁</div>
                    <div>
                        <h3 style={styles.cardTitle}>AI INTELLIGENCE</h3>
                        <p style={styles.cardText}>
                            Prediction, interpretation and AI-assisted decision support.
                        </p>
                    </div>
                </div>
            </section>

            {/* Architecture strip */}
            <section style={styles.pipeline}>
                <div style={styles.pipelineTitle}>GLYAB INTELLIGENCE PIPELINE</div>

                <div style={styles.pipelineRow}>
                    <span>DATA</span>
                    <b>→</b>
                    <span>FEATURES</span>
                    <b>→</b>
                    <span>ML ENGINE</span>
                    <b>→</b>
                    <span>RISK</span>
                    <b>→</b>
                    <span>AI COPILOT</span>
                </div>
            </section>

            {/* Footer */}
            <footer style={styles.footer}>
                <div>
                    <strong>GLYAB AI</strong>
                    <span> — Cryosphere Intelligence & GLOF Risk Assessment</span>
                </div>

                <div style={styles.footerRight}>
                    RESEARCH PROTOTYPE · ML ENABLED
                </div>
            </footer>
        </div>
    );
};

const styles: {
    [key: string]: React.CSSProperties;
} = {
    page: {
        minHeight: "100vh",
        position: "relative",
        overflow: "hidden",
        background:
            "radial-gradient(circle at 50% 10%, #102a46 0%, #06111f 35%, #020811 75%)",
        color: "#ffffff",
        fontFamily:
            "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
        padding: "0 6vw",
        boxSizing: "border-box",
    },

    glowOne: {
        position: "absolute",
        width: "420px",
        height: "420px",
        borderRadius: "50%",
        background: "rgba(48, 173, 255, 0.12)",
        filter: "blur(100px)",
        top: "-160px",
        left: "-100px",
        pointerEvents: "none",
    },

    glowTwo: {
        position: "absolute",
        width: "500px",
        height: "500px",
        borderRadius: "50%",
        background: "rgba(72, 226, 255, 0.08)",
        filter: "blur(120px)",
        bottom: "-250px",
        right: "-150px",
        pointerEvents: "none",
    },

    navbar: {
        position: "relative",
        zIndex: 2,
        height: "92px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        borderBottom: "1px solid rgba(255,255,255,0.08)",
    },

    logoBox: {
        display: "flex",
        alignItems: "center",
        gap: "12px",
    },

    logoMark: {
        width: "42px",
        height: "42px",
        borderRadius: "12px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background:
            "linear-gradient(135deg, #55d8ff 0%, #2678ff 100%)",
        color: "#03101c",
        fontSize: "22px",
        fontWeight: 900,
        boxShadow: "0 0 30px rgba(67, 194, 255, 0.25)",
    },

    logoText: {
        fontSize: "17px",
        fontWeight: 800,
        letterSpacing: "2px",
    },

    logoSub: {
        marginTop: "3px",
        fontSize: "8px",
        letterSpacing: "1.5px",
        color: "#6e91ae",
    },

    status: {
        display: "flex",
        alignItems: "center",
        gap: "8px",
        fontSize: "10px",
        letterSpacing: "1.5px",
        color: "#82a9c5",
    },

    statusDot: {
        width: "7px",
        height: "7px",
        borderRadius: "50%",
        background: "#46e6a3",
        boxShadow: "0 0 12px rgba(70,230,163,0.8)",
    },

    hero: {
        position: "relative",
        zIndex: 1,
        maxWidth: "950px",
        margin: "0 auto",
        textAlign: "center",
        padding: "105px 0 70px",
    },

    badge: {
        display: "inline-flex",
        alignItems: "center",
        gap: "9px",
        padding: "9px 15px",
        border: "1px solid rgba(86,207,255,0.25)",
        borderRadius: "999px",
        background: "rgba(20,70,100,0.18)",
        color: "#70cfff",
        fontSize: "10px",
        fontWeight: 700,
        letterSpacing: "1.8px",
    },

    title: {
        margin: "28px 0 0",
        fontSize: "clamp(52px, 8vw, 104px)",
        lineHeight: 0.95,
        letterSpacing: "-5px",
        fontWeight: 850,
    },

    gradientText: {
        background:
            "linear-gradient(90deg, #ffffff 10%, #63d7ff 55%, #4a9eff 100%)",
        WebkitBackgroundClip: "text",
        WebkitTextFillColor: "transparent",
    },

    description: {
        maxWidth: "760px",
        margin: "32px auto 0",
        color: "#bdd0df",
        fontSize: "18px",
        lineHeight: 1.7,
    },

    subDescription: {
        maxWidth: "700px",
        margin: "15px auto 0",
        color: "#66849c",
        fontSize: "13px",
        lineHeight: 1.7,
    },

    actions: {
        marginTop: "36px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: "25px",
        flexWrap: "wrap",
    },

    primaryButton: {
        border: "none",
        cursor: "pointer",
        padding: "16px 23px",
        borderRadius: "12px",
        background:
            "linear-gradient(135deg, #64dcff 0%, #287cff 100%)",
        color: "#03101c",
        fontWeight: 900,
        letterSpacing: "1.2px",
        fontSize: "12px",
        display: "flex",
        alignItems: "center",
        gap: "20px",
        boxShadow: "0 12px 40px rgba(39,135,255,0.25)",
    },

    arrow: {
        fontSize: "19px",
    },

    liveIndicator: {
        display: "flex",
        alignItems: "center",
        gap: "8px",
        color: "#7895aa",
        fontSize: "10px",
        letterSpacing: "1.3px",
    },

    liveDot: {
        width: "6px",
        height: "6px",
        borderRadius: "50%",
        background: "#54e0a5",
        boxShadow: "0 0 10px rgba(84,224,165,0.8)",
    },

    cardsSection: {
        position: "relative",
        zIndex: 1,
        maxWidth: "1050px",
        margin: "0 auto",
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gap: "16px",
    },

    card: {
        padding: "22px",
        display: "flex",
        gap: "15px",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: "16px",
        background: "rgba(10,28,45,0.65)",
        backdropFilter: "blur(12px)",
    },

    cardIcon: {
        width: "38px",
        height: "38px",
        flexShrink: 0,
        borderRadius: "10px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(68,185,255,0.12)",
        color: "#62d7ff",
        fontSize: "18px",
    },

    cardTitle: {
        margin: 0,
        fontSize: "11px",
        letterSpacing: "1.5px",
        color: "#bce8ff",
    },

    cardText: {
        margin: "8px 0 0",
        color: "#66859c",
        fontSize: "12px",
        lineHeight: 1.5,
    },

    pipeline: {
        position: "relative",
        zIndex: 1,
        maxWidth: "1050px",
        margin: "30px auto 0",
        padding: "20px",
        borderTop: "1px solid rgba(255,255,255,0.07)",
        borderBottom: "1px solid rgba(255,255,255,0.07)",
        textAlign: "center",
    },

    pipelineTitle: {
        color: "#4f7189",
        fontSize: "9px",
        letterSpacing: "2px",
        marginBottom: "14px",
    },

    pipelineRow: {
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        gap: "18px",
        flexWrap: "wrap",
        color: "#86b7d3",
        fontSize: "10px",
        letterSpacing: "1.3px",
    },

    footer: {
        position: "relative",
        zIndex: 1,
        maxWidth: "1050px",
        margin: "35px auto 0",
        paddingBottom: "28px",
        display: "flex",
        justifyContent: "space-between",
        gap: "20px",
        color: "#4d697e",
        fontSize: "9px",
        letterSpacing: "1px",
    },

    footerRight: {
        textAlign: "right",
    },
};

export default GlyabLanding;