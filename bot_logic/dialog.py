import random
import nltk
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
from bot_logic.cleaner import clear_phrase
from bot_logic.config import BOT_CONFIG

X_text = []
y = []

for intent, intent_data in BOT_CONFIG['intents'].items():
    for example in intent_data['examples']:
        X_text.append(example)
        y.append(intent)

vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 3))
X = vectorizer.fit_transform(X_text)
clf = LinearSVC()
clf.fit(X, y)

dialogues_structured = {}

def structure_dialogues():
    dialogues = []
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

    intent = clf.predict(vectorizer.transform([replica]))[0]

    for example in BOT_CONFIG['intents'][intent]['examples']:
        example = clear_phrase(example)
        distance = nltk.edit_distance(replica, example)
        if example and distance / len(example) <= 0.5:
            return intent

def get_answer_by_intent(intent):
    if intent in BOT_CONFIG['intents']:
        responses = BOT_CONFIG['intents'][intent]['responses']
        if responses:
            return random.choice(responses)

def get_failure_phrase():
    failure_phrases = BOT_CONFIG['failure_phrases']
    return random.choice(failure_phrases)


def generate_answer(replica):
    replica = clear_phrase(replica)
    words = set(replica.split(' '))
    mini_dataset = []

    # Составляем мини-набор данных, собирая вопросы и ответы, соответствующие словам из реплики
    for word in words:
        if word in dialogues_structured:
            mini_dataset += dialogues_structured[word]

    # Убираем повторы из мини-набора данных
    mini_dataset = list(set(mini_dataset))

    answers = []  # [[distance_weighted, question, answer]]

    for question, answer in mini_dataset:
        # Если разница в длине реплики и вопроса не слишком велика, считаем расстояние Левенштейна
        if abs(len(replica) - len(question)) / len(question) < 0.2:
            distance = nltk.edit_distance(replica, question)
            distance_weighted = distance / len(question)
            if distance_weighted < 0.2:
                answers.append([distance_weighted, question, answer])

    # Если есть подходящие ответы, выбираем наиболее релевантный
    if answers:
        return min(answers, key=lambda three: three[0])[2]

    return None

