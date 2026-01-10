"""
Views API para predicción de spam
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from spam_detector.predictor import SpamPredictor
import os

# Inicializar predictor global
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'static', 'modelo_spam.joblib')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'static', 'vectorizador.joblib')

predictor = None

def initialize_predictor():
    """Inicializa el predictor si no existe"""
    global predictor
    if predictor is None:
        try:
            predictor = SpamPredictor(MODEL_PATH, VECTORIZER_PATH)
        except Exception as e:
            print(f"Error inicializando predictor: {e}")
            predictor = None
    return predictor


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def predict_spam(request):
    """
    Endpoint para predecir si un email es spam
    
    POST /api/predict
    Body: {"email_content": "contenido del email..."}
    """
    # Manejar preflight CORS
    if request.method == "OPTIONS":
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    try:
        # Parsear JSON
        data = json.loads(request.body)
        email_content = data.get('email_content', '')
        
        if not email_content:
            return JsonResponse({
                "error": "No se proporcionó contenido del email"
            }, status=400)
        
        # Inicializar predictor si es necesario
        pred = initialize_predictor()
        
        if pred is None:
            return JsonResponse({
                "error": "No se pudieron cargar los modelos. Asegúrese de que modelo_spam.joblib y vectorizador.joblib estén en la carpeta static/"
            }, status=500)
        
        # Realizar predicción
        resultado = pred.predict(email_content)
        
        # Agregar métricas del modelo (valores de ejemplo del notebook 10)
        resultado['metricas_modelo'] = {
            'f1_score': 0.96,  # Ajustar con el valor real del notebook 10
            'accuracy': 0.97,
            'matriz_confusion': {
                'true_negatives': 1500,
                'false_positives': 50,
                'false_negatives': 30,
                'true_positives': 1420
            }
        }
        
        response = JsonResponse(resultado)
        response["Access-Control-Allow-Origin"] = "*"
        return response
        
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "JSON inválido"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "error": f"Error en el servidor: {str(e)}"
        }, status=500)


@require_http_methods(["GET"])
def health_check(request):
    """Endpoint para verificar que la API está funcionando"""
    pred = initialize_predictor()
    
    response_data = {
        "status": "ok",
        "models_loaded": pred is not None,
        "message": "API de detección de spam funcionando correctamente"
    }
    
    response = JsonResponse(response_data)
    response["Access-Control-Allow-Origin"] = "*"
    return response
