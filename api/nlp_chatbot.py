import pandas as pd
import nltk
nltk.download('punkt')
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

lemmatizer = WordNetLemmatizer()

def preprocess(text):
    tokens = word_tokenize(text.lower())
    lemmatized = [lemmatizer.lemmatize(token) for token in tokens if token.isalpha()]
    return ' '.join(lemmatized)

class HealthcareChatbot:
    def __init__(self, dataset_path):
        self.df = pd.read_csv(dataset_path)
        self.df['question_clean'] = self.df['question'].apply(preprocess)
        self.vectorizer = TfidfVectorizer()
        self.question_vectors = self.vectorizer.fit_transform(self.df['question_clean'])

    def get_response(self, user_input):
        user_input_clean = preprocess(user_input)
        user_vector = self.vectorizer.transform([user_input_clean])
        similarities = cosine_similarity(user_vector, self.question_vectors)

        max_score = similarities.max()
        best_match_index = similarities.argmax()

        if max_score < 0.3:
            return "Sorry, I don't understand. Please ask something related to healthcare."

        return self.df.iloc[best_match_index]['answer']
