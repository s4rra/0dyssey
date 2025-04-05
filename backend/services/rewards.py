class RewardSystem:
    BASE_POINTS = {
        1: 5,  # for MCQ
        2: 10,  # for Coding
        3: 7,  # for Fill-in
        4: 8   # for Dragdrop
    }

    SKILL_BONUS = {
        1: 1,  # Beginner
        2: 2,  # Intermediate
        3: 3   # Advanced
    }

    @staticmethod
    def calculate_points(question_type_id, is_correct, retry, time_taken, skill_level, avg_time):
        if not is_correct:
            return 0
    
        base = RewardSystem.BASE_POINTS.get(question_type_id, 0)
        skill_bonus = RewardSystem.SKILL_BONUS.get(skill_level, 0)
        retry_penalty = max(0, retry - 1)

        # Basic time bonus logic (based on average time passed in)
        time_bonus = 0
        if time_taken is not None and avg_time:
            if time_taken < avg_time * 0.5:
                time_bonus = 3
            elif time_taken < avg_time * 0.75:
                time_bonus = 2
            elif time_taken < avg_time:
                time_bonus = 1

        total = base + skill_bonus + time_bonus - retry_penalty
        total = max(total, 1)

        print(f"[POINTS DEBUG] Base: {base}, Skill Bonus: {skill_bonus}, Time Bonus: {time_bonus}, Retry Penalty: {retry_penalty}, Total: {total}")

        return total

