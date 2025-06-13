import pickle
import pandas as pd

# Load the pickle model
with open('./downloaded_models/model/model.pkl', 'rb') as f:
    model = pickle.load(f)

# Input data (excluding wine_id which is not a feature)
input_data = {
    "real_time_measurement": [3.1],
    "fixed_acidity": [7.4],
    "volatile_acidity": [0.7],
    "citric_acid": [0.0],
    "residual_sugar": [1.9],
    "chlorides": [0.076],
    "free_sulfur_dioxide": [11],
    "total_sulfur_dioxide": [34],
    "density": [0.9978],
    "pH": [3.51],
    "sulphates": [0.56],
    "alcohol": [9.4],
    "average_so2": [22.5],

}
print("Model feature names:", model.feature_names_in_)
# Convert to DataFrame
input_df = pd.DataFrame(input_data)

# Print the feature names to see what the model expects
print("Features being used:", list(input_df.columns))

# Make prediction
prediction = model.predict(input_df)

print(f"Prediction: {prediction[0]}")