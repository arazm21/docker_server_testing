import requests
import json

url = "http://127.0.0.1:5000/invocations"
headers = {"Content-Type": "application/json"}

data = {
    "inputs": [{

        "fixed_acidity": 7.4,
        "volatile_acidity": 0.7,
        "citric_acid": 0.0,
        "residual_sugar": 1.9,
        "chlorides": 0.076,
        "free_sulfur_dioxide": 11,
        "total_sulfur_dioxide": 34,
        "density": 0.9978,
        "pH": 3.51,
        "sulphates": 0.56,
        "alcohol": 9.4,

        "real_time_measurement": 3.1,
        "average_so2": 22.5,
    }]
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print("Prediction:", response.json())
