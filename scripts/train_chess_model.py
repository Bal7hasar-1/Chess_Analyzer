import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib


INPUT_CSV = "data/chess_features_dataset.csv"
OUTPUT_MODEL = "models/chess_error_model.joblib"

print(f"Loading data from {INPUT_CSV}...")
df = pd.read_csv(INPUT_CSV)


feature_columns = [
    "cp_loss", 
    "mat_diff", 
    "hanging_diff", 
    "mobility_diff", 
    "best_gives_check"
]

X = df[feature_columns]
y = df["error_class"]


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training dataset size: {len(X_train)} examples")
print(f"Test set size: {len(X_test)} examples\n")


model_pipeline = Pipeline(steps=[
    ("scaler", StandardScaler()),
    ("classifier", RandomForestClassifier(
        n_estimators=200, 
        max_depth=10, 
        random_state=42, 
        class_weight="balanced"
    ))
])


print("Training RandomForest...")
model_pipeline.fit(X_train, y_train)


print("\n=== TEST SET RESULTS ===")
y_pred = model_pipeline.predict(X_test)
print(classification_report(y_test, y_pred))


joblib.dump(model_pipeline, OUTPUT_MODEL)
print(f"\nModel successfully saved to a file: {OUTPUT_MODEL}")