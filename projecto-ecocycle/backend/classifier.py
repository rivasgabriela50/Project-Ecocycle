"""
Sistema de clasificación ML para análisis de prototipos sostenibles
Predice eficiencia, impacto ambiental y recomendaciones
"""

import numpy as np
import pickle
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum


class EcoCategory(Enum):
    """Categorías de clasificación ecológica"""
    MUY_EFICIENTE = "muy_eficiente"
    EFICIENTE = "eficiente"
    MODERADO = "moderado"
    BAJO = "bajo"
    CRITICO = "critico"


@dataclass
class ClassificationResult:
    """Resultado de clasificación"""
    categoria: str
    confianza: float
    score_eficiencia: float
    score_ambiental: float
    recomendaciones: List[str]
    metricas_predichas: Dict[str, float]


class EcocycleClassifier:
    """Clasificador de prototipos Ecocycle"""
    
    def __init__(self, model_path: str = None):
        """Inicializa el clasificador"""
        self.model_path = model_path
        self.model = None
        self.is_trained = False
        self.feature_names = [
            'potencia_entrada_w',
            'potencia_salida_w',
            'temperatura_operacion_c',
            'durabilidad_meses',
            'componentes_reciclables',
            'peso_kg',
            'costo_produccion_usd'
        ]
        self.load_or_init_model()
    
    def load_or_init_model(self):
        """Carga el modelo o inicializa uno de demostración"""
        if self.model_path and os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                self.is_trained = True
            except Exception as e:
                print(f"Error cargando modelo: {e}. Usando modelo de demostración.")
                self._init_demo_model()
        else:
            self._init_demo_model()
    
    def _init_demo_model(self):
        """Inicializa un modelo simple para demostración"""
        self.is_trained = True
        # Pesos de caracteristicas para scoring
        self.weights = {
            'potencia_entrada_w': -0.001,      # Menor entrada es mejor
            'potencia_salida_w': 0.002,        # Mayor salida es mejor
            'temperatura_operacion_c': -0.01,  # Menor temperatura es mejor
            'durabilidad_meses': 0.005,        # Mayor durabilidad es mejor
            'componentes_reciclables': 0.3,    # Más reciclables es mejor
            'peso_kg': -0.01,                  # Menor peso es mejor
            'costo_produccion_usd': -0.0001    # Menor costo es mejor
        }
    
    def predict(self, features: Dict[str, float]) -> ClassificationResult:
        """
        Clasifica un prototipo basado en sus características
        
        Args:
            features: Dict con valores de características
            
        Returns:
            ClassificationResult con predicción y análisis
        """
        # Validar características
        self._validate_features(features)
        
        # Calcular scores
        score_eficiencia = self._calculate_efficiency_score(features)
        score_ambiental = self._calculate_environmental_score(features)
        
        # Determinar categoría
        categoria = self._determine_category(score_eficiencia, score_ambiental)
        
        # Calcular confianza
        confianza = self._calculate_confidence(score_eficiencia, score_ambiental)
        
        # Generar recomendaciones
        recomendaciones = self._generate_recommendations(features, score_eficiencia, score_ambiental)
        
        # Predecir métricas
        metricas = self._predict_metrics(features, score_eficiencia, score_ambiental)
        
        return ClassificationResult(
            categoria=categoria.value,
            confianza=round(confianza, 3),
            score_eficiencia=round(score_eficiencia, 3),
            score_ambiental=round(score_ambiental, 3),
            recomendaciones=recomendaciones,
            metricas_predichas=metricas
        )
    
    def _validate_features(self, features: Dict[str, float]):
        """Valida que todas las características requeridas estén presentes"""
        missing = [f for f in self.feature_names if f not in features]
        if missing:
            raise ValueError(f"Características faltantes: {missing}")
        
        # Validar rangos razonables
        if features['potencia_entrada_w'] < 0:
            raise ValueError("Potencia de entrada no puede ser negativa")
        if features['potencia_salida_w'] < 0:
            raise ValueError("Potencia de salida no puede ser negativa")
        if features['durabilidad_meses'] < 0:
            raise ValueError("Durabilidad no puede ser negativa")
    
    def _calculate_efficiency_score(self, features: Dict[str, float]) -> float:
        """Calcula score de eficiencia (0-1)"""
        entrada = features['potencia_entrada_w']
        salida = features['potencia_salida_w']
        
        # Eficiencia = Salida / Entrada
        if entrada == 0:
            eficiencia = 0
        else:
            eficiencia = min(salida / entrada, 1.0)  # Max 100%
        
        # Factor de durabilidad (más durabilidad = mayor eficiencia sostenida)
        durabilidad_factor = min(features['durabilidad_meses'] / 60, 1.0)  # Ref: 60 meses
        
        score = (eficiencia * 0.6) + (durabilidad_factor * 0.4)
        return min(score, 1.0)
    
    def _calculate_environmental_score(self, features: Dict[str, float]) -> float:
        """Calcula score ambiental (0-1)"""
        # Componentes reciclables (0-100%) -> normalizar
        reciclaje_score = features['componentes_reciclables'] / 100.0
        
        # Temperatura (menor es mejor, ref: 80°C)
        temp_score = max(1 - (features['temperatura_operacion_c'] / 100), 0)
        
        # Peso (menor es mejor, ref: 50kg)
        peso_score = max(1 - (features['peso_kg'] / 100), 0)
        
        # Score ponderado
        score = (reciclaje_score * 0.5) + (temp_score * 0.3) + (peso_score * 0.2)
        return min(score, 1.0)
    
    def _determine_category(self, eff_score: float, env_score: float) -> EcoCategory:
        """Determina la categoría basada en scores"""
        combined_score = (eff_score * 0.6) + (env_score * 0.4)
        
        if combined_score >= 0.85:
            return EcoCategory.MUY_EFICIENTE
        elif combined_score >= 0.70:
            return EcoCategory.EFICIENTE
        elif combined_score >= 0.50:
            return EcoCategory.MODERADO
        elif combined_score >= 0.30:
            return EcoCategory.BAJO
        else:
            return EcoCategory.CRITICO
    
    def _calculate_confidence(self, eff_score: float, env_score: float) -> float:
        """Calcula el nivel de confianza de la predicción"""
        # Confianza es mayor cuando los scores están equilibrados
        diferencia = abs(eff_score - env_score)
        confianza_base = 1 - (diferencia * 0.2)
        
        # Aumentar confianza si el score combinado es más extremo
        combined = (eff_score + env_score) / 2
        if combined > 0.8 or combined < 0.2:
            confianza_base += 0.1
        
        return min(confianza_base, 1.0)
    
    def _generate_recommendations(self, features: Dict[str, float], 
                                 eff_score: float, env_score: float) -> List[str]:
        """Genera recomendaciones para mejorar el prototipo"""
        recomendaciones = []
        
        # Eficiencia
        if eff_score < 0.6:
            if features['potencia_salida_w'] < features['potencia_entrada_w'] * 0.75:
                recomendaciones.append("Optimizar conversión de energía - Considerar componentes de menor pérdida")
            if features['durabilidad_meses'] < 24:
                recomendaciones.append("Aumentar durabilidad - Usar materiales de mayor resistencia")
        
        # Ambiental
        if env_score < 0.6:
            if features['componentes_reciclables'] < 70:
                recomendaciones.append("Incrementar porcentaje de componentes reciclables")
            if features['temperatura_operacion_c'] > 80:
                recomendaciones.append("Mejorar sistema de disipación térmica")
            if features['peso_kg'] > 50:
                recomendaciones.append("Reducir peso usando materiales alternativos")
        
        # Costo
        if features['costo_produccion_usd'] > 1000:
            recomendaciones.append("Explorar economías de escala para reducir costo")
        
        if not recomendaciones:
            recomendaciones.append("Excelente rendimiento - Mantener estándares actuales")
        
        return recomendaciones
    
    def _predict_metrics(self, features: Dict[str, float], 
                        eff_score: float, env_score: float) -> Dict[str, float]:
        """Predice métricas de impacto"""
        
        # Energía ahorrada (kWh/año) - basado en eficiencia
        energia_ahorrada = (features['potencia_entrada_w'] / 1000) * eff_score * 8760  # horas/año
        
        # Emisiones reducidas (kg CO2/año) - basado en ambiental
        # Factor de emisión aproximado: 0.5 kg CO2 por kWh ahorrado
        emisiones_reducidas = energia_ahorrada * 0.5
        
        # Eficiencia porcentaje
        eficiencia_porcentaje = eff_score * 100
        
        # Autonomía estimada (horas) - basado en durabilidad
        autonomia_horas = features['durabilidad_meses'] * 30 * 24
        
        return {
            "energia_ahorrada_kwh": round(energia_ahorrada, 2),
            "emisiones_reducidas_kg": round(emisiones_reducidas, 2),
            "eficiencia_porcentaje": round(eficiencia_porcentaje, 2),
            "autonomia_horas": round(autonomia_horas, 2)
        }
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Retorna la importancia de cada característica"""
        return {
            'potencia_entrada_w': 0.15,
            'potencia_salida_w': 0.20,
            'temperatura_operacion_c': 0.15,
            'durabilidad_meses': 0.20,
            'componentes_reciclables': 0.15,
            'peso_kg': 0.10,
            'costo_produccion_usd': 0.05
        }
    
    def save_model(self, path: str):
        """Guarda el modelo entrenado"""
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
    
    @staticmethod
    def batch_predict(classifier, features_list: List[Dict]) -> List[ClassificationResult]:
        """Realiza predicciones en lote"""
        return [classifier.predict(features) for features in features_list]