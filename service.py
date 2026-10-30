
from models import ServiceError


class RiskEngine:
    def evaluate(self, rating, value_cents, account_age_days):
        if (
            type(rating) is not int
            or not 1 <= rating <= 5
            or type(value_cents) is not int
            or value_cents < 0
            or type(account_age_days) is not int
            or account_age_days < 0
        ):
            raise ServiceError(400, "invalid_input")

        rating_points = (5 - rating) * 10

        if value_cents >= 50000:
            value_points = 30
        elif value_cents >= 10000:
            value_points = 15
        else:
            value_points = 0

        if account_age_days < 30:
            age_points = 25
        elif account_age_days < 180:
            age_points = 10
        else:
            age_points = 0

        score = rating_points + value_points + age_points

        if score >= 60:
            decision = "reject"
        elif score >= 30:
            decision = "manual_review"
        else:
            decision = "approve"

        return {
            "score": score,
            "decision": decision,
            "components": {
                "rating": rating_points,
                "value": value_points,
                "age": age_points,
            },
        }

    def evaluate_many(self, records):
        results = []

        for record in records:
            try:
                if (
                    not isinstance(record, dict)
                    or set(record) != {
                        "rating",
                        "value_cents",
                        "account_age_days",
                    }
                ):
                    raise ServiceError(400, "invalid_input")

                result = self.evaluate(**record)
                results.append({"result": result, "error": None})

            except ServiceError:
                results.append({"result": None, "error": "invalid_input"})

        return results
