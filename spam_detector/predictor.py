"""
Predictor que carga los modelos y realiza predicciones
"""
import joblib
import os
from .parser import Parser


class SpamPredictor:
    """Clase para cargar modelos y hacer predicciones"""
    
    def __init__(self, model_path='static/modelo_spam.joblib', 
                 vectorizer_path='static/vectorizador.joblib'):
        """
        Inicializa el predictor cargando modelo y vectorizador
        """
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        self.parser = Parser()
        
        # Cargar modelo y vectorizador
        self.load_models()
    
    def load_models(self):
        """Carga los modelos desde archivos .joblib"""
        try:
            self.model = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)
            print(f"✓ Modelos cargados exitosamente")
        except Exception as e:
            print(f"✗ Error al cargar modelos: {e}")
            self.model = None
            self.vectorizer = None
    
    def predict(self, email_content):
        """
        Predice si un email es spam o ham
        
        Args:
            email_content: Contenido del email como string
            
        Returns:
            dict con resultado, probabilidad y tokens importantes
        """
        if not self.model or not self.vectorizer:
            return {
                "error": "Modelos no cargados",
                "resultado": "unknown",
                "probabilidad": 0.0
            }
        
        try:
            # Preprocesar el contenido
            features_text = self.parser.get_features_email(email_content)
            
            # Vectorizar
            X = self.vectorizer.transform([features_text])
            
            # Predecir
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            
            # Obtener palabras importantes
            important_words = self.get_important_words(features_text, X)
            
            # Determinar la clase y probabilidad
            if prediction == 1 or prediction == 'spam':
                resultado = "Spam"
                probabilidad = probabilities[1] if len(probabilities) > 1 else probabilities[0]
            else:
                resultado = "Ham"
                probabilidad = probabilities[0] if len(probabilities) > 1 else 1 - probabilities[0]
            
            return {
                "resultado": resultado,
                "probabilidad": float(probabilidad),
                "probabilidad_spam": float(probabilities[1]) if len(probabilities) > 1 else float(prediction),
                "probabilidad_ham": float(probabilities[0]) if len(probabilities) > 1 else float(1 - prediction),
                "palabras_importantes": important_words,
                "tokens_procesados": features_text.split()[:50]  # Primeros 50 tokens
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "resultado": "error",
                "probabilidad": 0.0
            }
    
    def get_important_words(self, features_text, X_vectorized, top_n=10):
        """
        Obtiene las palabras más importantes para la clasificación
        """
        try:
            # Obtener nombres de características
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Obtener coeficientes del modelo
            if hasattr(self.model, 'coef_'):
                coefficients = self.model.coef_[0]
                
                # Obtener índices de las palabras presentes en el documento
                word_indices = X_vectorized.nonzero()[1]
                
                # Calcular importancia
                word_importance = []
                for idx in word_indices:
                    word = feature_names[idx]
                    importance = abs(coefficients[idx] * X_vectorized[0, idx])
                    word_importance.append({
                        "palabra": word,
                        "importancia": float(importance)
                    })
                
                # Ordenar por importancia
                word_importance.sort(key=lambda x: x['importancia'], reverse=True)
                
                return word_importance[:top_n]
            else:
                # Si el modelo no tiene coef_, retornar las palabras más frecuentes
                tokens = features_text.split()
                from collections import Counter
                word_counts = Counter(tokens)
                return [
                    {"palabra": word, "importancia": count}
                    for word, count in word_counts.most_common(top_n)
                ]
                
        except Exception as e:
            print(f"Error obteniendo palabras importantes: {e}")
            return []
