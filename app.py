import gradio as gr
import joblib
import pandas as pd
import json
import os

# ---- File paths (using YOUR filenames) ----

MODEL_PATH = "Credit Risk Model.joblib"
FEATURES_PATH = "Feature Names from Pipeline.json"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Could not find model file at {MODEL_PATH}")

# Load the gradient boosting model
model = joblib.load(MODEL_PATH)

# Load the feature names (column order used during training)
try:
    with open(FEATURES_PATH, "r") as f:
        feature_names = json.load(f)
except FileNotFoundError:
    feature_names = None  # We'll handle this gracefully later.


def predict_default(csv_file):
    """
    csv_file: uploaded CSV with one or more client rows.
    Returns: DataFrame with predicted default probability and class.
    """

    if csv_file is None:
        return "Please upload a CSV file."

    # Read the uploaded CSV file
    df = pd.read_csv(csv_file.name)

    # If we know the expected feature names, align columns
    if feature_names is not None:
        missing = [col for col in feature_names if col not in df.columns]
        if missing:
            return (
                f"The uploaded CSV is missing these required columns: {missing}\n"
                f"Columns expected: {feature_names}"
            )
        # Reorder the columns to match training order
        df = df[feature_names]

    # Predict default probabilities and labels
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(df)[:, 1]  # probability of default (class = 1)
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
Upload a CSV file with one or more credit card clients using the same feature
columns as the training data (e.g., LIMIT_BAL, AGE, PAY_0, etc.).
The app will return the predicted probability of default (1)
and the predicted class for each row.
"""

demo = gr.Interface(
    fn=predict_default,
    inputs=gr.File(label="Upload client CSV"),
    outputs=gr.Dataframe(label="Predictions"),
    title="Credit Risk - Gradient Boosting Model",
    description=description_text,
)

if __name__ == "__main__":
    demo.launch()
