import React from "react";

const Local: React.FC = () => {
    return (
        <section
            style={{
                minHeight: "100vh",
                width: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: "#050b14",
                color: "white",
                padding: "40px",
                boxSizing: "border-box",
            }}
        >
            <div style={{ textAlign: "center" }}>
                <h1>GLYAB Local Intelligence</h1>

                <p>
                    Local analysis module is ready.
                </p>

                <div
                    style={{
                        marginTop: "30px",
                        padding: "25px",
                        border: "1px solid rgba(255,255,255,0.2)",
                        borderRadius: "16px",
                        background: "rgba(255,255,255,0.05)",
                    }}
                >
                    <h2>Local Analysis</h2>
                    <p>Remote sensing and AI analysis can be connected here.</p>
                </div>
            </div>
        </section>
    );
};

export default Local;