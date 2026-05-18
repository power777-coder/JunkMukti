import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# Load data
data = pd.read_csv("pricing_data.csv")

X = data[['waste_type', 'weight_kg']]
y = data['price']

# Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(), ['waste_type']),
        ('num', 'passthrough', ['weight_kg'])
    ]
)

# Model pipeline
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', LinearRegression())
])

# Train model
model.fit(X, y)

# Save model
joblib.dump(model, "price_model.pkl")

print("✅ ML model trained and saved")
