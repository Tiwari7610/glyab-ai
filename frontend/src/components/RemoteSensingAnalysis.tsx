import { useEffect, useMemo, useState } from "react";
import "./RemoteSensingAnalysis.css";

interface RemoteSensingAnalysisProps {
    onAnalysisComplete?: () => void;
}

type PipelineStatus =
    | "QUEUED"
    | "PROCESSING"
    | "COMPLETE";

const bands = [
    {
        name: "BLUE",
        value: "B02",
        wavelength: "490 nm",
    },
    {
        name: "GREEN",
        value: "B03",
        wavelength: "560 nm",
    },
    {
        name: "RED",
        value: "B04",
        wavelength: "665 nm",
    },
    {
        name: "NIR",
        value: "B08",
        wavelength: "842 nm",
    },
    {
        name: "SWIR",
        value: "B11",
        wavelength: "1610 nm",
    },
];

const pipeline = [
    "SATELLITE ACQUISITION",
    "RADIOMETRIC PROCESSING",
    "CLOUD MASKING",
    "TERRAIN EXTRACTION",
    "ICE / WATER SEGMENTATION",
    "AI FEATURE ENGINEERING",
];

const processingMessages = [
    "Establishing satellite data link...",
    "Receiving multispectral observation...",
    "Applying radiometric calibration...",
    "Generating cloud probability mask...",
    "Extracting terrain morphology...",
    "Computing spectral indices...",
    "Segmenting cryosphere features...",
    "Extracting glacier-lake boundaries...",
    "Engineering AI prediction features...",
    "Preparing GLYAB Intelligence Engine...",
];

const spectralData = {
    BLUE: [0.21, 0.25, 0.23, 0.28, 0.31, 0.27, 0.34, 0.29],
    GREEN: [0.28, 0.31, 0.35, 0.33, 0.39, 0.37, 0.42, 0.40],
    RED: [0.18, 0.21, 0.19, 0.24, 0.27, 0.22, 0.29, 0.25],
    NIR: [0.61, 0.67, 0.72, 0.69, 0.77, 0.74, 0.81, 0.79],
    SWIR: [0.32, 0.35, 0.31, 0.39, 0.42, 0.37, 0.45, 0.41],
};

function Sparkline({
    values,
    height = 54,
}: {
    values: number[];
    height?: number;
}) {
    const width = 260;

    const min = Math.min(...values);
    const max = Math.max(...values);

    const points = values
        .map((value, index) => {
            const x =
                (index / (values.length - 1)) *
                width;

            const normalized =
                max === min
                    ? 0.5
                    : (value - min) /
                    (max - min);

            const y =
                height -
                normalized * (height - 8) -
                4;

            return `${x},${y}`;
        })
        .join(" ");

    return (
        <svg
            viewBox={`0 0 ${width} ${height}`}
            preserveAspectRatio="none"
            className="rs-sparkline"
        >
            <polyline
                points={points}
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
            />

            {values.map((value, index) => {
                const x =
                    (index / (values.length - 1)) *
                    width;

                const normalized =
                    max === min
                        ? 0.5
                        : (value - min) /
                        (max - min);

                const y =
                    height -
                    normalized * (height - 8) -
                    4;

                return (
                    <circle
                        key={`${value}-${index}`}
                        cx={x}
                        cy={y}
                        r="2"
                        fill="currentColor"
                    />
                );
            })}
        </svg>
    );
}

function MetricCard({
    label,
    value,
    unit,
    status,
}: {
    label: string;
    value: string;
    unit?: string;
    status?: string;
}) {
    return (
        <div className="rs-metric-card">
            <div className="rs-metric-label">
                {label}
            </div>

            <div className="rs-metric-value">
                {value}

                {unit && (
                    <span>{unit}</span>
                )}
            </div>

            {status && (
                <div className="rs-metric-status">
                    <i />
                    {status}
                </div>
            )}
        </div>
    );
}

function PipelineStep({
    index,
    name,
    active,
    complete,
}: {
    index: number;
    name: string;
    active: boolean;
    complete: boolean;
}) {
    const status: PipelineStatus = complete
        ? "COMPLETE"
        : active
            ? "PROCESSING"
            : "QUEUED";

    return (
        <div
            className={[
                "rs-pipeline-step",
                active ? "active" : "",
                complete ? "complete" : "",
            ].join(" ")}
        >
            <div className="rs-pipeline-number">
                {String(index + 1).padStart(2, "0")}
            </div>

            <div className="rs-pipeline-content">
                <div className="rs-pipeline-name">
                    {name}
                </div>

                <div className="rs-pipeline-status">
                    {status}
                </div>
            </div>

            <div className="rs-pipeline-indicator">
                {complete
                    ? "✓"
                    : active
                        ? "●"
                        : "—"}
            </div>
        </div>
    );
}

export default function RemoteSensingAnalysis({
    onAnalysisComplete,
}: RemoteSensingAnalysisProps) {
    const [progress, setProgress] =
        useState(0);

    const [activeBand, setActiveBand] =
        useState(0);

    const [activePipeline, setActivePipeline] =
        useState(0);

    const [scanPosition, setScanPosition] =
        useState(0);

    const [selectedBand, setSelectedBand] =
        useState("NIR");

    const [analysisComplete, setAnalysisComplete] =
        useState(false);

    const [messageIndex, setMessageIndex] =
        useState(0);

    const [targetLocked, setTargetLocked] =
        useState(false);

    const [acquisitionTime, setAcquisitionTime] =
        useState(0);

    const [pixelCount, setPixelCount] =
        useState(0);

    /*
     * =========================================================
     * MAIN REMOTE-SENSING PROCESS
     * =========================================================
     */

    useEffect(() => {
        if (analysisComplete) {
            return;
        }

        const progressTimer =
            window.setInterval(() => {
                setProgress((previous) => {
                    if (previous >= 100) {
                        window.clearInterval(
                            progressTimer
                        );

                        setAnalysisComplete(true);

                        window.setTimeout(() => {
                            onAnalysisComplete?.();
                        }, 1400);

                        return 100;
                    }

                    return previous + 1;
                });
            }, 90);

        return () => {
            window.clearInterval(
                progressTimer
            );
        };
    }, [
        analysisComplete,
        onAnalysisComplete,
    ]);

    /*
     * =========================================================
     * BAND ROTATION
     * =========================================================
     */

    useEffect(() => {
        if (analysisComplete) {
            return;
        }

        const timer =
            window.setInterval(() => {
                setActiveBand((previous) => {
                    const next =
                        (previous + 1) %
                        bands.length;

                    setSelectedBand(
                        bands[next].name
                    );

                    return next;
                });
            }, 1200);

        return () =>
            window.clearInterval(timer);
    }, [analysisComplete]);

    /*
     * =========================================================
     * PIPELINE
     * =========================================================
     */

    useEffect(() => {
        if (analysisComplete) {
            return;
        }

        const timer =
            window.setInterval(() => {
                setActivePipeline(
                    (previous) =>
                        Math.min(
                            previous + 1,
                            pipeline.length - 1
                        )
                );
            }, 1500);

        return () =>
            window.clearInterval(timer);
    }, [analysisComplete]);

    /*
     * =========================================================
     * SCAN BEAM
     * =========================================================
     */

    useEffect(() => {
        const timer =
            window.setInterval(() => {
                setScanPosition((previous) => {
                    if (previous >= 100) {
                        return 0;
                    }

                    return previous + 1.8;
                });
            }, 40);

        return () =>
            window.clearInterval(timer);
    }, []);

    /*
     * =========================================================
     * TARGET LOCK
     * =========================================================
     */

    useEffect(() => {
        const timer =
            window.setTimeout(() => {
                setTargetLocked(true);
            }, 2300);

        return () =>
            window.clearTimeout(timer);
    }, []);

    /*
     * =========================================================
     * PROCESSING MESSAGE
     * =========================================================
     */

    useEffect(() => {
        const timer =
            window.setInterval(() => {
                setMessageIndex(
                    (previous) =>
                        (previous + 1) %
                        processingMessages.length
                );
            }, 1100);

        return () =>
            window.clearInterval(timer);
    }, []);

    /*
     * =========================================================
     * TELEMETRY
     * =========================================================
     */

    useEffect(() => {
        const timer =
            window.setInterval(() => {
                setAcquisitionTime(
                    (previous) =>
                        previous + 1
                );

                setPixelCount(
                    (previous) =>
                        Math.min(
                            previous + 18427,
                            9845321
                        )
                );
            }, 500);

        return () =>
            window.clearInterval(timer);
    }, []);

    /*
     * =========================================================
     * CURRENT BAND
     * =========================================================
     */

    const currentBand =
        bands[activeBand];

    /*
     * =========================================================
     * ACTIVE SPECTRAL DATA
     * =========================================================
     */

    const currentSpectralData =
        useMemo(() => {
            return (
                spectralData[
                selectedBand as keyof typeof spectralData
                ] ??
                spectralData.NIR
            );
        }, [selectedBand]);

    /*
     * =========================================================
     * SPECTRAL INDICES
     *
     * Demonstration formulas:
     *
     * NDVI = (NIR - RED)/(NIR + RED)
     *
     * NDWI = (GREEN - NIR)/(GREEN + NIR)
     *
     * NDSI = (GREEN - SWIR)/(GREEN + SWIR)
     *
     * These are UI-side prototype calculations.
     * Real raster pixels will later come from backend.
     * =========================================================
     */

    const ndvi = 0.74;
    const ndwi = 0.61;
    const ndsi = 0.82;

    const cloudCoverage = 7.4;

    const elevation = 4870;

    const slope = 31.6;

    const glacierArea = 18.42;

    const lakeArea = 2.73;

    /*
     * =========================================================
     * PIPELINE COMPLETION
     * =========================================================
     */

    const completedSteps =
        analysisComplete
            ? pipeline.length
            : activePipeline;

    return (
        <main className="remote-analysis">

            {/* =================================================
                TOP COMMAND HEADER
            ================================================= */}

            <header className="analysis-header">

                <div className="brand-block">

                    <div className="brand-mark">
                        G
                    </div>

                    <div>
                        <div className="brand-name">
                            GLYAB
                        </div>

                        <div className="brand-subtitle">
                            CRYOSPHERE INTELLIGENCE SYSTEM
                        </div>
                    </div>

                </div>


                <div className="mission-status">

                    <span
                        className={
                            analysisComplete
                                ? "status-dot complete"
                                : "status-dot"
                        }
                    />

                    <span>
                        REMOTE SENSING PIPELINE
                    </span>

                    <strong>
                        {analysisComplete
                            ? "COMPLETE"
                            : "PROCESSING"}
                    </strong>

                </div>


                <div className="mission-time">

                    <span>
                        MISSION / RS-001
                    </span>

                    <strong>
                        HIMALAYAN CRYOSPHERE
                    </strong>

                </div>

            </header>


            {/* =================================================
                MISSION INFORMATION STRIP
            ================================================= */}

            <section className="mission-strip">

                <div>
                    <span>PLATFORM</span>
                    <strong>
                        EARTH OBSERVATION
                    </strong>
                </div>

                <div>
                    <span>TARGET</span>
                    <strong>
                        HIMALAYAN SECTOR
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
                    <span>ALTITUDE</span>
                    <strong>
                        4,870 M
                    </strong>
                </div>

                <div>
                    <span>MODE</span>
                    <strong>
                        MULTISPECTRAL
                    </strong>
                </div>

            </section>


            {/* =================================================
                MAIN GRID
            ================================================= */}

            <section className="analysis-grid">

                {/* =============================================
                    LEFT CONTROL PANEL
                ============================================== */}

                <aside className="analysis-sidebar">

                    <div className="panel-label">
                        TARGET IDENTIFICATION
                    </div>

                    <div className="target-name">
                        HIMALAYAN SECTOR
                    </div>

                    <div className="target-state">

                        <span
                            className={
                                targetLocked
                                    ? "lock-icon locked"
                                    : "lock-icon"
                            }
                        >
                            {targetLocked
                                ? "⌾"
                                : "○"}
                        </span>

                        <div>
                            <strong>
                                {targetLocked
                                    ? "TARGET LOCKED"
                                    : "ACQUIRING TARGET"}
                            </strong>

                            <small>
                                GEOREFERENCED WINDOW
                            </small>
                        </div>

                    </div>


                    <div className="target-coordinates">

                        <div>
                            <span>LAT</span>
                            <strong>
                                30.421°
                            </strong>
                            <small>N</small>
                        </div>

                        <div>
                            <span>LON</span>
                            <strong>
                                79.208°
                            </strong>
                            <small>E</small>
                        </div>

                        <div>
                            <span>ALT</span>
                            <strong>
                                4,870
                            </strong>
                            <small>M</small>
                        </div>

                    </div>


                    <div className="separator" />


                    {/* SENSOR */}

                    <div className="panel-label">
                        SENSOR CONFIGURATION
                    </div>

                    <div className="band-list">

                        {bands.map(
                            (band, index) => (
                                <button
                                    type="button"
                                    key={band.value}
                                    className={
                                        index ===
                                            activeBand
                                            ? "band-row active"
                                            : "band-row"
                                    }
                                    onClick={() =>
                                        setSelectedBand(
                                            band.name
                                        )
                                    }
                                >

                                    <div className="band-name">
                                        {band.name}
                                    </div>

                                    <div className="band-value">
                                        {band.value}
                                    </div>

                                    <div className="band-wavelength">
                                        {band.wavelength}
                                    </div>

                                    <div className="band-status">
                                        ●
                                    </div>

                                </button>
                            )
                        )}

                    </div>


                    <div className="separator" />


                    {/* SOURCE */}

                    <div className="panel-label">
                        DATA SOURCE
                    </div>

                    <div className="data-source">

                        <strong>
                            OPTICAL / MULTISPECTRAL
                        </strong>

                        <span>
                            EARTH OBSERVATION DATA
                        </span>

                    </div>

                    <div className="data-source">

                        <strong>
                            GEOSPATIAL GRID
                        </strong>

                        <span>
                            HIMALAYAN TARGET WINDOW
                        </span>

                    </div>


                    <div className="data-source">

                        <strong>
                            PROCESSING MODE
                        </strong>

                        <span>
                            CRYOSPHERE ANALYTICS
                        </span>

                    </div>

                </aside>


                {/* =============================================
                    CENTRAL TERRAIN INTELLIGENCE
                ============================================== */}

                <section className="analysis-core">

                    <div className="core-header">

                        <div>

                            <span className="eyebrow">
                                REMOTE SENSING
                            </span>

                            <h1>
                                TERRAIN
                                <br />
                                INTELLIGENCE
                            </h1>

                        </div>

                        <div className="scene-id">

                            <span>
                                SCENE
                            </span>

                            <strong>
                                HML-30N79E
                            </strong>

                            <small>
                                ACQUISITION WINDOW
                            </small>

                        </div>

                    </div>


                    {/* =========================================
                        SATELLITE VIEW
                    ========================================== */}

                    <div className="satellite-view">

                        <div className="viewport-corner tl" />
                        <div className="viewport-corner tr" />
                        <div className="viewport-corner bl" />
                        <div className="viewport-corner br" />


                        <div className="grid-overlay" />


                        {/* contour lines */}

                        <div className="contour contour-1" />
                        <div className="contour contour-2" />
                        <div className="contour contour-3" />
                        <div className="contour contour-4" />


                        {/* mountain terrain */}

                        <div className="terrain-map">

                            <div className="mountain mountain-one" />

                            <div className="mountain mountain-two" />

                            <div className="mountain mountain-three" />

                            <div className="mountain mountain-four" />

                            <div className="mountain mountain-five" />


                            {/* glacier */}

                            <div className="glacier-zone">

                                <div className="ice-ridge" />

                                <div className="ice-ridge second" />

                                <div className="ice-ridge third" />

                            </div>


                            {/* lake */}

                            <div className="water-body">

                                <span>
                                    GLACIAL LAKE
                                </span>

                                <small>
                                    2.73 KM²
                                </small>

                            </div>


                            {/* moraine */}

                            <div className="moraine-zone">
                                MORAINE
                            </div>

                        </div>


                        {/* scan beam */}

                        <div
                            className="scan-line"
                            style={{
                                top: `${scanPosition}%`,
                            }}
                        />

                        <div className="scan-pulse" />


                        {/* target box */}

                        <div className="target-box">

                            <span className="corner c1" />
                            <span className="corner c2" />
                            <span className="corner c3" />
                            <span className="corner c4" />

                            <div className="target-crosshair">
                                <span />
                                <span />
                            </div>

                        </div>


                        {/* feature labels */}

                        <div className="scene-label glacier-label">

                            <i />

                            ICE MASS

                            <span>
                                DETECTED
                            </span>

                        </div>


                        <div className="scene-label lake-label">

                            <i />

                            WATER BODY

                            <span>
                                DETECTED
                            </span>

                        </div>


                        <div className="scene-label terrain-label">

                            <i />

                            TERRAIN

                            <span>
                                ANALYZING
                            </span>

                        </div>


                        {/* coordinates */}

                        <div className="scene-coordinate top-coordinate">
                            30°25'16"N
                        </div>

                        <div className="scene-coordinate bottom-coordinate">
                            79°12'28"E
                        </div>


                        {/* sensor info */}

                        <div className="scene-overlay-info">

                            <span>
                                BAND
                            </span>

                            <strong>
                                {currentBand.value}
                            </strong>

                            <small>
                                {currentBand.wavelength}
                            </small>

                        </div>


                        {/* scene footer */}

                        <div className="scene-footer">

                            <span>
                                SENSOR: MULTISPECTRAL
                            </span>

                            <span>
                                GRID: 10m ANALYSIS
                            </span>

                            <span>
                                MODE: CRYOSPHERE
                            </span>

                            <span>
                                TARGET:
                                {targetLocked
                                    ? " LOCKED"
                                    : " ACQUIRING"}
                            </span>

                        </div>

                    </div>


                    {/* =========================================
                        METRICS
                    ========================================== */}

                    <div className="metric-grid">

                        <MetricCard
                            label="ELEVATION"
                            value={elevation.toString()}
                            unit=" M"
                            status="TERRAIN"
                        />

                        <MetricCard
                            label="SLOPE"
                            value={slope.toString()}
                            unit="°"
                            status="DERIVED"
                        />

                        <MetricCard
                            label="GLACIER AREA"
                            value={glacierArea.toString()}
                            unit=" KM²"
                            status="SEGMENTED"
                        />

                        <MetricCard
                            label="LAKE AREA"
                            value={lakeArea.toString()}
                            unit=" KM²"
                            status="DETECTED"
                        />

                        <MetricCard
                            label="CLOUD COVER"
                            value={cloudCoverage.toString()}
                            unit="%"
                            status="MASKED"
                        />

                    </div>


                    {/* =========================================
                        PROCESSING PIPELINE
                    ========================================== */}

                    <div className="processing-block">

                        <div className="processing-heading">

                            <div>

                                <span>
                                    ANALYSIS PIPELINE
                                </span>

                                <small>
                                    {processingMessages[
                                        messageIndex
                                    ]}
                                </small>

                            </div>

                            <strong>
                                {progress
                                    .toString()
                                    .padStart(3, "0")}
                                %
                            </strong>

                        </div>


                        <div className="progress-track">

                            <div
                                className="progress-fill"
                                style={{
                                    width:
                                        `${progress}%`,
                                }}
                            />

                        </div>

                        <div className="progress-meta">

                            <span>
                                PROCESSING
                            </span>

                            <span>
                                {completedSteps}/
                                {pipeline.length}
                                MODULES
                            </span>

                        </div>

                    </div>

                </section>


                {/* =============================================
                    RIGHT INTELLIGENCE PANEL
                ============================================== */}

                <aside className="ai-panel">

                    <div className="panel-label">
                        GLYAB INTELLIGENCE CORE
                    </div>


                    {/* AI CORE */}

                    <div className="ai-state">

                        <div className="ai-core-circle">

                            <div className="ai-core-orbit" />

                            <div className="ai-core-inner">
                                AI
                            </div>

                        </div>

                        <div>

                            <strong>
                                ANALYSIS ENGINE
                            </strong>

                            <span>
                                {analysisComplete
                                    ? "FEATURES VALIDATED"
                                    : "PIPELINE INITIALIZED"}
                            </span>

                        </div>

                    </div>


                    <div className="separator" />


                    {/* PIPELINE */}

                    <div className="panel-label">
                        PROCESSING PIPELINE
                    </div>

                    <div className="pipeline-list">

                        {pipeline.map(
                            (step, index) => (
                                <PipelineStep
                                    key={step}
                                    index={index}
                                    name={step}
                                    active={
                                        index ===
                                        activePipeline &&
                                        !analysisComplete
                                    }
                                    complete={
                                        analysisComplete ||
                                        index <
                                        activePipeline
                                    }
                                />
                            )
                        )}

                    </div>


                    <div className="separator" />


                    {/* FEATURES */}

                    <div className="feature-card">

                        <div className="feature-title">
                            DETECTED FEATURES
                        </div>

                        <div className="feature-row">

                            <span>
                                ICE COVER
                            </span>

                            <strong>
                                DETECTED
                            </strong>

                        </div>

                        <div className="feature-row">

                            <span>
                                WATER BODY
                            </span>

                            <strong>
                                DETECTED
                            </strong>

                        </div>

                        <div className="feature-row">

                            <span>
                                TERRAIN
                            </span>

                            <strong>
                                DERIVED
                            </strong>

                        </div>

                        <div className="feature-row">

                            <span>
                                CLOUD MASK
                            </span>

                            <strong>
                                {cloudCoverage}%
                            </strong>

                        </div>

                    </div>


                    {/* =========================================
                        SPECTRAL INDICES
                    ========================================== */}

                    <div className="spectral-card">

                        <div className="feature-title">
                            SPECTRAL INDICES
                        </div>

                        <div className="index-row">

                            <div>
                                <span>
                                    NDVI
                                </span>

                                <small>
                                    VEGETATION
                                </small>
                            </div>

                            <strong>
                                {ndvi.toFixed(2)}
                            </strong>

                        </div>

                        <div className="index-row">

                            <div>
                                <span>
                                    NDWI
                                </span>

                                <small>
                                    WATER
                                </small>
                            </div>

                            <strong>
                                {ndwi.toFixed(2)}
                            </strong>

                        </div>

                        <div className="index-row">

                            <div>
                                <span>
                                    NDSI
                                </span>

                                <small>
                                    SNOW / ICE
                                </small>
                            </div>

                            <strong>
                                {ndsi.toFixed(2)}
                            </strong>

                        </div>

                    </div>


                    {/* =========================================
                        SPECTRAL SIGNATURE
                    ========================================== */}

                    <div className="spectral-signature">

                        <div className="feature-title">

                            SPECTRAL SIGNATURE

                            <span>
                                {selectedBand}
                            </span>

                        </div>

                        <Sparkline
                            values={
                                currentSpectralData
                            }
                        />

                        <div className="spectral-scale">

                            <span>
                                LOW
                            </span>

                            <span>
                                REFLECTANCE
                            </span>

                            <span>
                                HIGH
                            </span>

                        </div>

                    </div>


                    {/* MODEL STATUS */}

                    <div className="model-notice">

                        <span>
                            AI MODEL STATUS
                        </span>

                        <strong>
                            {analysisComplete
                                ? "FEATURES READY"
                                : "WAITING FOR FEATURES"}
                        </strong>

                        <small>
                            {analysisComplete
                                ? "Validated remote-sensing features are ready for the GLYAB prediction engine."
                                : "Prediction engine activates after validated environmental features are available."}
                        </small>

                    </div>

                </aside>

            </section>


            {/* =================================================
                BOTTOM TELEMETRY
            ================================================= */}

            <footer className="analysis-footer">

                <div>
                    <span>
                        ACQUISITION
                    </span>

                    <strong>
                        {acquisitionTime}s
                    </strong>
                </div>

                <div>
                    <span>
                        PIXELS
                    </span>

                    <strong>
                        {pixelCount.toLocaleString()}
                    </strong>
                </div>

                <div>
                    <span>
                        SCAN
                    </span>

                    <strong>
                        ACTIVE
                    </strong>
                </div>

                <div>
                    <span>
                        ICE SEGMENTATION
                    </span>

                    <strong>
                        READY
                    </strong>
                </div>

                <div>
                    <span>
                        WATER EXTRACTION
                    </span>

                    <strong>
                        READY
                    </strong>
                </div>

                <div>
                    <span>
                        AI RISK ENGINE
                    </span>

                    <strong>
                        {analysisComplete
                            ? "READY"
                            : "STANDBY"}
                    </strong>
                </div>

                <div>
                    <span>
                        DATA LINK
                    </span>

                    <strong>
                        LOCAL PIPELINE
                    </strong>
                </div>

            </footer>

        </main>
    );
}