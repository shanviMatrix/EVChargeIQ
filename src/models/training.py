import numpy as np
from src.config import FEATURE_COLUMNS, TARGET_COLUMN
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

def train_models(model_data):

    train_data = model_data[
        model_data["year_index"] <= 2
    ].copy()

    test_data = model_data[
        model_data["year_index"] == 3
    ].copy()

    if train_data.empty or test_data.empty:

        raise ValueError(
            "Insufficient historical data for "
            "chronological model evaluation."
        )

    categorical_features = [
        "state"
    ]

    numeric_features = [
        "year_index",
        "current_installations",
        "cumulative_installations",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "state",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features,
            ),

            (
                "numeric",
                Pipeline(
                    steps=[
                        (
                            "imputer",
                            SimpleImputer(
                                strategy="median"
                            ),
                        ),

                        (
                            "scaler",
                            StandardScaler(),
                        ),
                    ]
                ),
                numeric_features,
            ),
        ]
    )

    model_definitions = {

        "Linear Regression":
            LinearRegression(),

        "Decision Tree":
            DecisionTreeRegressor(
                max_depth=5,
                random_state=42,
            ),

        "Random Forest":
            RandomForestRegressor(
                n_estimators=150,
                max_depth=6,
                random_state=42,
            ),
    }

    x_train = train_data[FEATURE_COLUMNS]

    y_train = train_data[TARGET_COLUMN]

    x_test = test_data[FEATURE_COLUMNS]

    y_test = test_data[TARGET_COLUMN]

    fitted_models = {}

    result_rows = []

    prediction_frames = {}

    for model_name, estimator in model_definitions.items():

        pipeline = Pipeline(
            steps=[
                (
                    "preprocessing",
                    preprocessor,
                ),

                (
                    "model",
                    estimator,
                ),
            ]
        )

        pipeline.fit(
            x_train,
            y_train,
        )

        raw_predictions = pipeline.predict(
            x_test
        )

        predictions = np.maximum(
            raw_predictions,
            0,
        )

        fitted_models[model_name] = pipeline

        result_rows.append(
            {
                "Model": model_name,

                "MAE": mean_absolute_error(
                    y_test,
                    predictions,
                ),

                "RMSE": np.sqrt(
                    mean_squared_error(
                        y_test,
                        predictions,
                    )
                ),

                "R²": r2_score(
                    y_test,
                    predictions,
                ),
            }
        )

        prediction_frames[model_name] = pd.DataFrame(
            {
                "State": test_data["state"].values,

                "Actual installations": y_test.values,

                "Predicted installations": predictions,
            }
        )

    results = pd.DataFrame(
        result_rows
    ).sort_values(
        "MAE",
        ascending=True,
    )

    return (
        fitted_models,
        results,
        prediction_frames,
        train_data,
        test_data,
    )
