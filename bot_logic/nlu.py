from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from bot_logic.cleaner import clear_phrase
from bot_logic.config import BOT_CONFIG

def load_dialogues(path='dialogues.txt'):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    dialogues_str = content.split('\n\n')
    dialogues = [d.split('\n')[:2] for d in dialogues_str]

    dialogues_filtered = []
    questions = set()

    for d in dialogues:
        if len(d) != 2:
            continue
        question = clear_phrase(d[0][2:])
        answer = d[1][2:]

        if question and question not in questions:
            questions.add(question)
            dialogues_filtered.append([question, answer])

    return dialogues_filtered

dialogues = load_dialogues()
questions = [q for q, _ in dialogues]
answers = [a for _, a in dialogues]

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(questions)

def get_intent(user_message: str):
    user_message = user_message.lower()

    for intent_name, intent_data in BOT_CONFIG['intents'].items():
        for example in intent_data['examples']:
            if example.lower() in user_message:
                return intent_name
    return None

def get_ml_answer(user_text: str, threshold: float = 0.3):
    if not questions:
        load_dialogues()
    user_vector = vectorizer.transform([user_text])
    similarities = cosine_similarity(user_vector, tfidf_matrix)[0]
    best_idx = similarities.argmax()
    best_score = similarities[best_idx]
    best_answer = answers[best_idx]

    # 🔍 Отбрасываем плохие совпадения
    if best_score < threshold:
        return None

    answer = best_answer.strip().strip('"').strip()
    answer = answer[0].upper() + answer[1:] if answer else answer
    if answer and answer[-1] not in ".!?…":
        answer += "."

    return answer