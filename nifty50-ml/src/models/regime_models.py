class RegimeModels:
    def __init__(self):
        self.low = None
        self.mid = None
        self.high = None

    def predict(self, regime, features):
        # placeholder: plug real trained models here
        if regime == "low":
            return 0.52
        if regime == "mid":
            return 0.6
        return 0.68
