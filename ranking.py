def calculate_score(worker):
    score = 0

    score += worker.completed_jobs * 2
    score += worker.rating

    return score