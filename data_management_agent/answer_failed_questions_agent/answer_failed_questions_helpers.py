import random
from shared_clients.chroma_client import failed_questions_collection
from shared_clients.supabase_client import supabase
from chroma.chroma_helpers import insert_resume_fact

def get_brand_agent_id_from_asi_one_id(asi_one_id: str) -> str:
    """
    Gets the personal brand agent ID from the ASI:One ID.
    Args:
        asi_one_id: The ASI:One ID
    Returns:
        The personal brand agent ID
    """
    result = supabase.table("personal_brand_asi_one_relationships").select("personal_brand_agent_id").eq("asi_one_id", asi_one_id).execute()
    return result.data[0]["personal_brand_agent_id"] if result.data else None # type: ignore

def get_all_failed_questions(personal_brand_agent_id: str) -> list[dict]:
    """
    Gets all failed questions for a personal brand agent.
    Args:
        personal_brand_agent_id: The personal brand agent ID
    Returns:
        List of dicts with keys: id, document, metadata
    """
    results = failed_questions_collection.get(
        where={"personal_brand_agent_id": personal_brand_agent_id}
    )
    
    questions = []
    if results['ids']:
        for i, question_id in enumerate(results['ids']):
            questions.append({
                "id": question_id,
                "question": results['documents'][i] if results['documents'] else "",
                "metadata": results['metadatas'][i] if results['metadatas'] else {}
            })
    
    return questions

def get_question_by_id(question_id: str) -> dict | None:
    """
    Gets a question by its ID.
    Args:
        question_id: The question ID
    Returns:
        Dict with id, question, metadata or None if not found
    """
    results = failed_questions_collection.get(ids=[question_id])
    
    if results['ids'] and len(results['ids']) > 0:
        return {
            "id": results['ids'][0],
            "question": results['documents'][0] if results['documents'] else "",
            "metadata": results['metadatas'][0] if results['metadatas'] else {}
        }
    
    return None

def get_random_question(personal_brand_agent_id: str) -> dict | None:
    """
    Gets a random failed question for a personal brand agent.
    Args:
        personal_brand_agent_id: The personal brand agent ID
    Returns:
        Dict with id, question, metadata or None if no questions found
    """
    questions = get_all_failed_questions(personal_brand_agent_id)
    
    if not questions:
        return None
    
    return random.choice(questions)

def delete_question(question_id: str):
    """
    Deletes a question from the failed questions collection.
    Args:
        question_id: The question ID to delete
    """
    failed_questions_collection.delete(ids=[question_id])

def format_questions_list(questions: list[dict], limit: int = None) -> str:
    """
    Formats a list of questions for display.
    Args:
        questions: List of question dicts
        limit: Optional limit on number of questions to show
    Returns:
        Formatted string
    """
    if not questions:
        return "No failed questions found."
    
    if limit:
        questions = questions[:limit]
    
    formatted = []
    for q in questions:
        formatted.append(f"ID: {q['id']}\nQuestion: {q['question']}")
    
    return "\n\n".join(formatted)

def save_answer_as_fact(asi_one_id: str, question: str, answer: str):
    """
    Saves the user's answer as a fact in the facts collection.
    Args:
        asi_one_id: The ASI:One ID
        question: The question that was answered
        answer: The user's answer
    """
    fact = f"Q: {question}\nA: {answer}"
    insert_resume_fact(asi_one_id, fact)

