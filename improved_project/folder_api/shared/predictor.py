class WineQualityPredictor:
    def __init__(self, db_client, model_client):
        self.db_client = db_client
        self.model_client = model_client

    def predict_quality(self, wine_id: int, real_time_measurement: float) -> float:
        # Step 1: Fetch features
        wine_features = self.db_client.get_wine_features(wine_id)

        # print("here1")
        
        # Step 2: Merge real-time measurement
        full_features = {**wine_features, "real_time_measurement": real_time_measurement}

        # print("here2")


        # Step 3: Predict
        prediction = self.model_client.predict(full_features)

        # print("here3")


        return prediction
