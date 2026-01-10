"""
Paquete spam_detector para detección de spam
"""
from .parser import Parser
from .predictor import SpamPredictor

__all__ = ['Parser', 'SpamPredictor']
