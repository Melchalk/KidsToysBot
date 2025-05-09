import random
import nltk
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from bot_logic.cleaner import clear_phrase
from bot_logic.config import BOT_CONFIG
from bot_logic.nlu import get_ml_answer, get_intent

X_text = []
y = []

for global_intent, global_intent_data in BOT_CONFIG['intents'].items():
    for global_example in global_intent_data['examples']:
        X_text.append(global_example)
        y.append(global_intent)

vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 3))
X = vectorizer.fit_transform(X_text)
clf = LinearSVC()
clf.fit(X, y)

dialogues_structured = {}

ads_counter = 0
ads_next_trigger = random.randint(*BOT_CONFIG['ads_interval'])

def structure_dialogues():
    for intent, intent_data in BOT_CONFIG['intents'].items():
        for example in intent_data['examples']:
            question = clear_phrase(example)
            answer = random.choice(intent_data['responses'])
            words = set(question.split(' '))
            for word in words:
                if word not in dialogues_structured:
                    dialogues_structured[word] = []
                dialogues_structured[word].append([question, answer])

def classify_intent(replica):
    replica = clear_phrase(replica)

    choice_intent = clf.predict(vectorizer.transform([replica]))[0]

    for example in BOT_CONFIG['intents'][choice_intent]['examples']:
        example = clear_phrase(example)
        distance = nltk.edit_distance(replica, example)
        if example and distance / len(example) <= 0.5:
            return choice_intent

def get_answer_by_intent(intent):
    if intent in BOT_CONFIG['intents']:
        responses = BOT_CONFIG['intents'][intent]['responses']
        if responses:
            return random.choice(responses)

def get_failure_phrase():
    failure_phrases = BOT_CONFIG['failure_phrases']
    return random.choice(failure_phrases)

def generate_answer(user_message: str):
    global ads_counter, ads_next_trigger

    temp_intent = get_intent(user_message)
    if temp_intent:
        return random.choice(BOT_CONFIG['intents'][temp_intent]['responses'])

    ml_answer = get_ml_answer(user_message)
    if ml_answer:
        return ml_answer

    return random.choice(BOT_CONFIG['failure_phrases'])

