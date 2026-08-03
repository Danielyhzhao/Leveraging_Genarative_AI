# metrics.py
# Metrics Tracking

class OptimizationMetrics:
    def __init__(self, problem_desc: str):
        self.pass_rates = []
        self.difficulty = self.classify_difficulty(problem_desc)  # PDF p.15

    def classify_difficulty(self, problem_desc: str) -> str:
        # Placeholder: Use keywords or NLP to classify (easy/medium/hard)
        if "easy" in problem_desc.lower():
            return "easy"
        elif "hard" in problem_desc.lower():
            return "hard"
        return "medium"

    def track_pass_rate(self, test_result):
        self.pass_rates.append(test_result.pass_rate)

    def get_stats(self) -> dict:
        if not self.pass_rates:
            return {"improvement": 0.0}
        improvement = self.pass_rates[-1] - self.pass_rates[0] if len(self.pass_rates) > 1 else 0.0
        return {
            "initial_pass_rate": self.pass_rates[0],
            "final_pass_rate": self.pass_rates[-1],
            "improvement": improvement,
            "difficulty": self.difficulty,
            # Extend for distribution analysis (PDF p.14-15)
        }