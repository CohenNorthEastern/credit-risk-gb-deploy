import gradio as gr
import joblib
import pandas as pd
import json
import os

# ---- File paths ----
MODEL_PATH = "Credit Risk Model.joblib"
FEATURES_PATH = "Feature Names from Pipeline.json"

# Basic check to ensure model exists
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Could not find model file at {MODEL_PATH}")

# Load the trained model
model = joblib.load(MODEL_PATH)

# Load feature names if available (to ensure correct column order)
try:
    with open(FEATURES_PATH, "r") as f:
        feature_names = json.load(f)
except FileNotFoundError:
    feature_names = None 


def predict_default(csv_file):
    """
    csv_file: uploaded CSV with one or more client rows.
    Returns: DataFrame with predicted default probability and class.
    """
    if csv_file is None:
        return "Please upload a CSV file."

    # Read the uploaded CSV file
    df = pd.read_csv(csv_file.name)

    # If we have specific feature names from training, enforce that order
    if feature_names is not None:
        # Check for missing columns
        missing = [col for col in feature_names if col not in df.columns]
        if missing:
            return (
                f"Error: The uploaded CSV is missing these required columns: {missing}\n"
                f"Columns expected: {feature_names}"
            )
        # Reorder columns to match training data exactly
        df = df[feature_names]

    # Predict default probabilities (if supported) and labels
    if hasattr(model, "predict_proba"):
        # Probability of class 1 (Default)
        proba = model.predict_proba(df)[:, 1]
    else:
        proba = None

    preds = model.predict(df)

    # Build result table
    result = df.copy()
    if proba is not None:
        result["default_probability"] = proba
    result["default_prediction"] = preds

    return result


# ---- Gradio UI ----

description_text = """
# Credit Risk Gradient Boosting Model

**Instructions:**
1. Upload a CSV file containing client data.
2. The file must include the feature columns used during training (e.g., `LIMIT_BAL`, `AGE`, `PAY_0`, `BILL_AMT1`, etc.).
3. The app will return the original data with two new columns: 
   - `default_probability`: The likelihood of default.
   - `default_prediction`: 0 (No Default) or 1 (Default).
"""

demo = gr.Interface(
    fn=predict_default,
    inputs=gr.File(label="Upload Client CSV"),
    outputs=gr.Dataframe(label="Predictions"),
    title="Credit Risk Prediction",
    description=description_text,
)

if __name__ == "__main__":
    demo.launch()
