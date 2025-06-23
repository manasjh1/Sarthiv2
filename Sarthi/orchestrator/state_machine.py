from prompts.prompt_library import prompt_library

def get_next_stage(current_stage: int):
    next_stage = current_stage + 1
    if next_stage not in prompt_library:
        return None
    return {
        "stage_no": next_stage,
        "stage_name": prompt_library[next_stage]["name"],
        "prompt": prompt_library[next_stage]["prompt"]
    }