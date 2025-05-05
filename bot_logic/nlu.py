import nltk
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from bot_logic.config import BOT_CONFIG
from bot_logic.cleaner import clear_phrase

class IntentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 3))
        self.clf = LinearSVC()

        self._train()

    def _train(self):
        X_text = []
        y = []

        for intent, data in BOT_CONFIG['intents'].items():
            for example in data['examples']:
                X_text.append(example)
                y.append(intent)

        X = self.vectorizer.fit_transform(X_text)
        self.clf.fit(X, y)

    def classify(self, phrase: str):
        phrase_clean = clear_phrase(phrase)

        predicted_intent = self.clf.predict(self.vectorizer.transform([phrase_clean]))[0]

        for example in BOT_CONFIG['intents'][predicted_intent]['examples']:
            example_clean = clear_phrase(example)
            if example_clean and nltk.edit_distance(phrase_clean, example_clean) / len(example_clean) < 0.4:
                return predicted_intent

        return None
