import re
import unicodedata
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize, TweetTokenizer
from nltk.stem import PorterStemmer, SnowballStemmer, WordNetLemmatizer
from nltk import pos_tag

# Pastikan resource NLTK tersedia
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')
    nltk.download('omw-1.4')

class TextPreprocessor:
    INDONESIAN_STOPWORDS = {
        'yang', 'untuk', 'pada', 'ke', 'para', 'namun', 'menurut', 'antara', 'dia', 'dua', 
        'ia', 'seperti', 'jika', 'jika', 'sehingga', 'kembali', 'dan', 'tidak', 'ini', 
        'karena', 'kepada', 'oleh', 'saat', 'harus', 'sementara', 'setelah', 'belum', 
        'kami', 'sekitar', 'bagi', 'serta', 'daripada', 'jauh', 'setiap', 'bagi', 'dahulu',
        'sesudah', 'sampai', 'sedang', 'juga', 'lihat', 'mungkin', 'sebagai', 'telah', 
        'adalah', 'tentang', 'dengan', 'ia', 'bahwa', 'oleh', 'itu', 'di', 'dari', 'tersebut'
    }

    def __init__(self, language='english'):
        self.language = language
        try:
            self.stop_words = set(stopwords.words(language))
        except Exception:
            self.stop_words = set()
        
        if language == 'indonesian' or not self.stop_words:
            self.stop_words.update(self.INDONESIAN_STOPWORDS)

    def transform(self, text, lowercase=True, remove_accents=True, parse_html=True, remove_urls=True):
        """1. Transformation Stage"""
        if parse_html:
            text = BeautifulSoup(text, "html.parser").get_text()
        
        if lowercase:
            text = text.lower()
            
        if remove_accents:
            text = ''.join(c for c in unicodedata.normalize('NFD', text)
                          if unicodedata.category(c) != 'Mn')
            
        if remove_urls:
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            
        return text

    def tokenize(self, text, method='word'):
        """2. Tokenization Stage"""
        if method == 'whitespace':
            return text.split()
        elif method == 'sentence':
            return sent_tokenize(text)
        elif method == 'tweet':
            return TweetTokenizer().tokenize(text)
        else: # Default Word
            return word_tokenize(text)

    def tag_pos(self, tokens):
        """3. POS Tagging"""
        return pos_tag(tokens)

    def normalize(self, tokens, method='lemmatizer'):
        """4. Normalization Stage"""
        if method == 'porter':
            stemmer = PorterStemmer()
            return [stemmer.stem(t) for t in tokens]
        elif method == 'snowball':
            stemmer = SnowballStemmer(self.language)
            return [stemmer.stem(t) for t in tokens]
        elif method == 'lemmatizer':
            lemmatizer = WordNetLemmatizer()
            # Lemmatizer butuh POS tag untuk hasil maksimal
            return [lemmatizer.lemmatize(t) for t in tokens]
        return tokens

    def filter_tokens(self, tokens, remove_stopwords=True, min_len=2):
        """5. Filtering Stage"""
        filtered = tokens
        if remove_stopwords:
            filtered = [t for t in filtered if t.lower() not in self.stop_words]
        
        # Filter by regex (only words) & length
        filtered = [t for t in filtered if re.match(r'^\w+$', t) and len(t) >= min_len]
        return filtered

    def generate_ngrams(self, tokens, n=2):
        """6. N-grams Stage"""
        return list(nltk.ngrams(tokens, n))

    def full_process(self, text):
        """Pipeline lengkap sesuai deskripsi user"""
        t = self.transform(text)
        tokens = self.tokenize(t)
        # filtered = self.filter_tokens(tokens) # Opsional: bersihkan dulu sebelum normalisasi
        normalized = self.normalize(tokens)
        final = self.filter_tokens(normalized)
        return final
