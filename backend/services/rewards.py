"""from datetime import datetime
import json

class ScoreCalculator:
    BASE_POINTS = {
        1: 5,  # MCQ
        2: 10,  # Coding
        3: 7,  # Fill-in
        4: 8   # Drag-drop
    }

    SKILL_BONUS = {
        1: 1,  # Beginner
        2: 2,  # Intermediate
        3: 3   # Advanced
    }

    @staticmethod
    def calculate_points(question_type_id, is_correct, retry, time_taken, skill_level, avg_time, base_score=None):
        if not is_correct:
            return 0

        base = base_score if base_score is not None else ScoreCalculator.BASE_POINTS.get(question_type_id, 0)
        skill_bonus = ScoreCalculator.SKILL_BONUS.get(skill_level, 0)
        retry_penalty = max(0, retry - 1)

        time_bonus = 0
        if time_taken is not None and avg_time:
            if time_taken < avg_time * 0.5:
                time_bonus = 3
            elif time_taken < avg_time * 0.75:
                time_bonus = 2
            elif time_taken < avg_time:
                time_bonus = 1

        total = base + skill_bonus + time_bonus - retry_penalty
        return max(total, 1)

"""