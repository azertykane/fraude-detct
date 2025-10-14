# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import numpy as np
import joblib
from io import BytesIO
import math

app = Flask(__name__)
app.secret_key = "secret_key_amelioree_2025"

# --- Charger le modèle RandomForest ---
MODEL_PATH = "rf_model.pkl"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("rf_model.pkl non trouvé dans le dossier du projet")
model = joblib.load(MODEL_PATH)

# --- Colonnes originales du CSV ---
EXPECTED_COLUMNS = [
    "Gender", "Age", "HouseTypeID", "ContactAvaliabilityID", "HomeCountry",
    "AccountNo", "CardExpiryDate", "TransactionAmount", "TransactionCountry",
    "LargePurchase", "ProductID", "CIF", "TransactionCurrencyCode", "PotentialFraud"
]

# --- Types et contraintes pour la validation ---
FIELD_TYPES = {
    "Gender": {"type": "int", "min": 0, "max": 1, "label": "Genre (0=Femme, 1=Homme)"},
    "Age": {"type": "int", "min": 18, "max": 100, "label": "Âge"},
    "HouseTypeID": {"type": "int", "min": 1, "max": 5, "label": "Type de logement"},
    "ContactAvaliabilityID": {"type": "int", "min": 1, "max": 3, "label": "Disponibilité contact"},
    "HomeCountry": {"type": "int", "min": 1, "max": 50, "label": "Pays d'origine"},
    "AccountNo": {"type": "int", "min": 100000, "max": 999999, "label": "Numéro de compte"},
    "CardExpiryDate": {"type": "int", "min": 202401, "max": 203012, "label": "Date d'expiration (AAAAMM)"},
    "TransactionAmount": {"type": "float", "min": 0.01, "max": 1000000, "label": "Montant de transaction"},
    "TransactionCountry": {"type": "int", "min": 1, "max": 50, "label": "Pays de transaction"},
    "LargePurchase": {"type": "int", "min": 0, "max": 1, "label": "Achat important (0=Non, 1=Oui)"},
    "ProductID": {"type": "int", "min": 1, "max": 20, "label": "ID Produit"},
    "CIF": {"type": "int", "min": 1000, "max": 9999, "label": "Code CIF"},
    "TransactionCurrencyCode": {"type": "int", "min": 1, "max": 10, "label": "Code devise"}
}

# --- Prétraitement identique à l'entraînement ---
def preprocess_df(df):
    df = df.copy()

    expected_features = [
        "Gender", "Age", "HouseTypeID", "ContactAvaliabilityID", "HomeCountry",
        "AccountNo", "CardExpiryDate", "TransactionAmount", "TransactionCountry",
        "LargePurchase", "ProductID", "CIF", "TransactionCurrencyCode"
    ]

    # Ajout des colonnes manquantes
    for col in expected_features:
        if col not in df.columns:
            df[col] = 0

    # Garder l'ordre exact
    df = df[expected_features]

    # Conversion en numérique
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Transformation log du montant
    if "TransactionAmount" in df.columns:
        df["TransactionAmount"] = np.log1p(df["TransactionAmount"])

    return df

# --- Validation des données manuelles ---
def validate_manual_input(data):
    errors = {}
    
    for field, value in data.items():
        if field == "PotentialFraud":
            continue
            
        if not value:
            errors[field] = "Ce champ est obligatoire"
            continue
            
        field_info = FIELD_TYPES.get(field, {})
        
        try:
            if field_info.get("type") == "int":
                int_value = int(value)
                if "min" in field_info and int_value < field_info["min"]:
                    errors[field] = f"Minimum {field_info['min']}"
                if "max" in field_info and int_value > field_info["max"]:
                    errors[field] = f"Maximum {field_info['max']}"
                    
            elif field_info.get("type") == "float":
                float_value = float(value)
                if "min" in field_info and float_value < field_info["min"]:
                    errors[field] = f"Minimum {field_info['min']}"
                if "max" in field_info and float_value > field_info["max"]:
                    errors[field] = f"Maximum {field_info['max']}"
                    
        except ValueError:
            errors[field] = f"Doit être un {field_info.get('type', 'nombre')}"
    
    return errors

# Stockage temporaire des résultats (en mémoire)
results_data = {}

# --- Routes principales ---
@app.route("/")
def index():
    return render_template("index.html", expected_columns=EXPECTED_COLUMNS)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("❌ Aucun fichier envoyé", "danger")
        return redirect(url_for("index"))
    
    file = request.files["file"]
    if file.filename == "":
        flash("❌ Aucun fichier sélectionné", "danger")
        return redirect(url_for("index"))

    try:
        df = pd.read_csv(file)
        
        # Vérifier les colonnes requises
        missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
        if missing_cols:
            flash(f"⚠️ Colonnes manquantes: {', '.join(missing_cols)}", "warning")
        
    except Exception as e:
        flash(f"❌ Erreur lecture CSV: {e}", "danger")
        return redirect(url_for("index"))

    # Faire les prédictions
    X = preprocess_df(df)
    preds = model.predict(X)
    
    # Stocker les prédictions séparément
    df_without_predictions = df.copy()
    predictions_dict = {i: int(pred) for i, pred in enumerate(preds)}

    # Stocker les résultats avec un ID unique
    import uuid
    results_id = str(uuid.uuid4())
    results_data[results_id] = {
        'df': df_without_predictions,
        'predictions': predictions_dict,
        'csv_data': df_without_predictions.to_csv(index=False),
        'total_rows': len(df),
        'fraud_count': int(preds.sum()),
        'normal_count': len(df) - int(preds.sum())
    }

    print(f"✅ Prédictions stockées pour {len(df)} lignes, ID: {results_id}")

    return redirect(url_for("results", results_id=results_id, page=1))

@app.route("/results")
def results():
    results_id = request.args.get('results_id')
    page = request.args.get('page', 1, type=int)
    
    if not results_id or results_id not in results_data:
        flash("❌ Aucune donnée de résultat disponible", "danger")
        return redirect(url_for("index"))
    
    # Récupérer les données
    data = results_data[results_id]
    df = data['df']
    
    # Pagination - 100 lignes par page
    per_page = 100
    total_rows = data['total_rows']
    total_pages = math.ceil(total_rows / per_page)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    current_page_data = df.iloc[start_idx:end_idx]
    
    # Statistiques
    fraud_count = data['fraud_count']
    normal_count = data['normal_count']

    return render_template(
        "result.html",
        tables=[current_page_data.to_html(classes="table table-striped table-hover", index=False)],
        csv_data=data['csv_data'],
        current_page=page,
        total_pages=total_pages,
        total_rows=total_rows,
        fraud_count=fraud_count,
        normal_count=normal_count,
        per_page=per_page,
        results_id=results_id
    )

# Route pour obtenir la prédiction d'une ligne spécifique
@app.route("/get_prediction/<results_id>/<int:row_index>")
def get_prediction(results_id, row_index):
    print(f"🔍 Demande de prédiction pour results_id: {results_id}, row_index: {row_index}")
    
    if results_id not in results_data:
        return jsonify({"error": "Résultats non trouvés"}), 404
    
    predictions = results_data[results_id]['predictions']
    
    if row_index not in predictions:
        return jsonify({"error": "Ligne non trouvée"}), 404
    
    prediction = predictions[row_index]
    
    return jsonify({
        "prediction": prediction,
        "message": "💥 FRAUDE DÉTECTÉE" if prediction == 1 else "✅ Transaction normale"
    })

@app.route("/predict_manual", methods=["POST"])
def predict_manual():
    form_data = {col: request.form.get(col, "") for col in EXPECTED_COLUMNS if col != "PotentialFraud"}
    
    # Validation
    errors = validate_manual_input(form_data)
    
    if errors:
        return render_template(
            "manual_input.html",
            errors=errors,
            form_data=form_data,
            field_types=FIELD_TYPES,
            expected_columns=EXPECTED_COLUMNS
        )
    
    # Prédiction
    row = pd.DataFrame([form_data])
    X = preprocess_df(row)
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0].tolist() if hasattr(model, "predict_proba") else None
    
    result_color = "danger" if pred == 1 else "success"
    result_icon = "💥" if pred == 1 else "✅"
    result_text = "FRAUDE DÉTECTÉE" if pred == 1 else "Transaction normale"
    
    return render_template(
        "manual_input.html",
        result={
            "prediction": int(pred), 
            "proba": proba,
            "color": result_color,
            "icon": result_icon,
            "text": result_text
        },
        form_data=form_data,
        field_types=FIELD_TYPES,
        expected_columns=EXPECTED_COLUMNS
    )

@app.route("/manual")
def manual():
    return render_template(
        "manual_input.html", 
        field_types=FIELD_TYPES,
        expected_columns=EXPECTED_COLUMNS
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)