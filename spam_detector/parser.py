"""
Parser para preprocesamiento de correos electrónicos
Basado en el archivo 09_Creacion_de_tranformadores-y_pipelines-personalizados
"""
import email
import string
import nltk
from html.parser import HTMLParser
from nltk.corpus import stopwords

# Descargar stopwords si no están disponibles
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class MLStripper(HTMLParser):
    """Clase para eliminar etiquetas HTML"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    """Elimina las etiquetas HTML del texto"""
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class Parser:
    """
    Parser para preprocesar correos electrónicos
    Usa PorterStemmer y limpieza de HTML igual que en el entrenamiento
    """
    def __init__(self):
        self.stemmer = nltk.PorterStemmer()
        self.stopwords = set(stopwords.words('english'))
        self.punctuation = list(string.punctuation)

    def parse_text(self, text):
        """Parse texto plano (para contenido cargado desde el frontend)"""
        return self.tokenize(text)

    def parse_email(self, email_content):
        """Parse un correo completo desde string"""
        try:
            msg = email.message_from_string(email_content)
            return self.get_email_content(msg)
        except Exception as e:
            # Si falla el parsing como email, intentar como texto plano
            return {
                "subject": [],
                "body": self.tokenize(email_content),
                "content_type": "text/plain"
            }

    def get_email_content(self, msg):
        """Extrae el contenido del email"""
        subject = self.tokenize(msg['Subject']) if msg['Subject'] else []
        body = self.get_email_body(msg.get_payload(), msg.get_content_type())
        content_type = msg.get_content_type()
        
        return {
            "subject": subject,
            "body": body,
            "content_type": content_type
        }

    def get_email_body(self, payload, content_type):
        """Extrae el cuerpo del email"""
        body = []
        if isinstance(payload, str) and content_type == 'text/plain':
            return self.tokenize(payload)
        elif isinstance(payload, str) and content_type == 'text/html':
            return self.tokenize(strip_tags(payload))
        elif isinstance(payload, list):
            for p in payload:
                body += self.get_email_body(
                    p.get_payload(),
                    p.get_content_type()
                )
        return body

    def tokenize(self, text):
        """
        Transforma texto en tokens.
        Limpia puntuación y hace stemming.
        """
        if not text:
            return []
        
        # Limpiar puntuación
        for c in self.punctuation:
            text = text.replace(c, "")
        text = text.replace("\t", " ")
        text = text.replace("\n", " ")

        # Tokenizar
        tokens = list(filter(None, text.split(" ")))
        
        # Stemming y filtrar stopwords
        return [
            self.stemmer.stem(w.lower()) 
            for w in tokens 
            if w.lower() not in self.stopwords
        ]

    def get_features_text(self, text):
        """Obtiene las características de un texto plano"""
        tokens = self.tokenize(text)
        return " ".join(tokens)

    def get_features_email(self, email_content):
        """Obtiene las características de un email completo"""
        parsed = self.parse_email(email_content)
        all_tokens = parsed['subject'] + parsed['body']
        return " ".join(all_tokens)
