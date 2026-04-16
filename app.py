from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import joblib
from datetime import datetime

app = Flask(__name__)
app.secret_key = "inventory_forecast_demo_secret_key"

model = joblib.load("xgb_sales_model.pkl")
aggregates = joblib.load("aggregates.pkl")


def build_features(store: int, item: int, date_str: str) -> pd.DataFrame:
    date = pd.to_datetime(date_str)

    day = date.day
    month = date.month
    year = date.year
    dayofweek = date.dayofweek
    is_weekend = 1 if dayofweek in [5, 6] else 0

    global_mean = aggregates["global_mean"]

    row = {
        "store": store,
        "item": item,
        "day": day,
        "month": month,
        "year": year,
        "dayofweek": dayofweek,
        "is_weekend": is_weekend,
        "store_avg": aggregates["store_avg"].get(store, global_mean),
        "item_avg": aggregates["item_avg"].get(item, global_mean),
        "store_item_avg": aggregates["store_item_avg"].get(str((store, item)), global_mean),
        "dow_avg": aggregates["dow_avg"].get(dayofweek, global_mean),
        "month_avg": aggregates["month_avg"].get(month, global_mean),
        "store_dow_avg": aggregates["store_dow_avg"].get(str((store, dayofweek)), global_mean),
        "item_dow_avg": aggregates["item_dow_avg"].get(str((item, dayofweek)), global_mean),
    }

    columns = [
        "store",
        "item",
        "day",
        "month",
        "year",
        "dayofweek",
        "is_weekend",
        "store_avg",
        "item_avg",
        "store_item_avg",
        "dow_avg",
        "month_avg",
        "store_dow_avg",
        "item_dow_avg",
    ]

    return pd.DataFrame([row], columns=columns)


def add_prediction_to_history(store, item, date_str, prediction):
    history = session.get("prediction_history", [])

    history.insert(0, {
        "store": store,
        "item": item,
        "date": date_str,
        "prediction": round(float(prediction), 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    session["prediction_history"] = history[:5]


@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    error = None
    form_data = {"store": "", "item": "", "date": ""}
    prediction_history = session.get("prediction_history", [])

    if request.method == "POST":
        try:
            form_data["store"] = request.form.get("store", "").strip()
            form_data["item"] = request.form.get("item", "").strip()
            form_data["date"] = request.form.get("date", "").strip()

            store = int(form_data["store"])
            item = int(form_data["item"])
            date_str = form_data["date"]

            if store < 1 or item < 1:
                raise ValueError("Store ID and Item ID must be greater than 0.")

            features = build_features(store, item, date_str)
            prediction = float(model.predict(features)[0])

            add_prediction_to_history(store, item, date_str, prediction)
            prediction_history = session.get("prediction_history", [])

        except Exception as exc:
            error = f"Prediction failed: {exc}"

    return render_template(
        "index.html",
        prediction=prediction,
        error=error,
        form_data=form_data,
        prediction_history=prediction_history,
        rmse="7.25",
        mape="13.11%",
        accuracy="86.89%"
    )


@app.route("/predict", methods=["POST"])
def predict_api():
    try:
        data = request.get_json()

        store = int(data["store"])
        item = int(data["item"])
        date_str = data["date"]

        if store < 1 or item < 1:
            return jsonify({"error": "Store ID and Item ID must be greater than 0."}), 400

        features = build_features(store, item, date_str)
        prediction = float(model.predict(features)[0])

        return jsonify({
            "store": store,
            "item": item,
            "date": date_str,
            "predicted_sales": round(prediction, 2)
        })

    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": True,
        "aggregates_loaded": True
    })


if __name__ == "__main__":
    app.run(debug=True)