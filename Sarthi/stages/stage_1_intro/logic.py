async def determine_mode(proficiency_score: int) -> str:
    return "guided" if proficiency_score < 3 else "collaborative"