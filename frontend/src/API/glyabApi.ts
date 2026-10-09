const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export interface GLOFPredictionInput {
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

export interface GLOFPrediction {
    prediction: number;
    risk_level: string;
    risk_probability: number;
    risk_percentage: number;
    model: string;
}

export interface GLOFResponse {
    success: boolean;
    system: string;
    service: string;
    prediction: GLOFPrediction;
}

export async function predictGLOF(
    input: GLOFPredictionInput
): Promise<GLOFResponse> {
    const response = await fetch(
        `${API_BASE_URL}/glof/predict`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(input),
        }
    );

    if (!response.ok) {
        const errorText = await response.text();

        throw new Error(
            `GLOF API Error ${response.status}: ${errorText}`
        );
    }

    return response.json();
}


export async function checkBackendHealth() {
    const response = await fetch(
        `${API_BASE_URL}/glof/health`
    );

    if (!response.ok) {
        throw new Error("GLYAB backend is offline");
    }

    return response.json();
}