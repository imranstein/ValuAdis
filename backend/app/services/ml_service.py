"""
ValuAdis Machine Learning Service
Ethiopian Property Valuation Prediction Engine

This service provides ML-powered property value predictions
using historical data and Ethiopian market trends.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.data.models.property import Property
from app.data.models.valuation import Valuation

logger = logging.getLogger(__name__)

class EthiopianPropertyMLService:
    """
    Machine Learning service for Ethiopian property valuation predictions.
    
    Features:
    - Market trend analysis
    - Property value predictions
    - Anomaly detection
    - Municipality-specific models
    - Ethiopian compliance integration
    """
    
    def __init__(self):
        self.municipality_models = {}
        self.property_type_weights = {
            'residential': 1.0,
            'commercial': 1.2,
            'agricultural': 0.6,
            'industrial': 1.5,
            'mixed_use': 1.1
        }
        
        # Ethiopian market factors
        self.inflation_rate = 0.30  # 30% annual inflation in Ethiopia
        self.urban_growth_rate = 0.05  # 5% annual urban growth
        self.market_volatility = 0.15  # Market volatility factor
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models for different municipalities and property types."""
        # In a production environment, this would load trained models
        # For now, we'll use rule-based models with statistical factors
        
        # Municipality-specific factors based on Ethiopian market data
        self.municipality_factors = {
            'Addis Ababa': {
                'base_multiplier': 1.5,
                'growth_rate': 0.08,
                'demand_factor': 1.2,
                'infrastructure_score': 0.9
            },
            'Dire Dawa': {
                'base_multiplier': 1.2,
                'growth_rate': 0.06,
                'demand_factor': 1.0,
                'infrastructure_score': 0.7
            },
            'Mekelle': {
                'base_multiplier': 1.0,
                'growth_rate': 0.07,
                'demand_factor': 0.9,
                'infrastructure_score': 0.8
            },
            'Bahir Dar': {
                'base_multiplier': 1.1,
                'growth_rate': 0.09,
                'demand_factor': 1.1,
                'infrastructure_score': 0.8
            },
            'Adama': {
                'base_multiplier': 0.9,
                'growth_rate': 0.08,
                'demand_factor': 0.8,
                'infrastructure_score': 0.7
            },
            'Hawassa': {
                'base_multiplier': 1.0,
                'growth_rate': 0.10,
                'demand_factor': 1.0,
                'infrastructure_score': 0.7
            },
            'Gonder': {
                'base_multiplier': 0.8,
                'growth_rate': 0.05,
                'demand_factor': 0.7,
                'infrastructure_score': 0.6
            },
            'Jimma': {
                'base_multiplier': 0.8,
                'growth_rate': 0.06,
                'demand_factor': 0.7,
                'infrastructure_score': 0.6
            }
        }
    
    def predict_property_value(
        self,
        db: Session,
        property_data: Dict,
        prediction_horizon: int = 12
    ) -> Dict:
        """
        Predict property value for the next N months.
        
        Args:
            db: Database session
            property_data: Property details
            prediction_horizon: Number of months to predict
            
        Returns:
            Dictionary with predictions and confidence scores
        """
        try:
            # Get historical data for similar properties
            historical_data = self._get_historical_data(db, property_data)
            
            # Calculate base prediction
            base_prediction = self._calculate_base_prediction(property_data, historical_data)
            
            # Apply market trends
            market_adjusted_prediction = self._apply_market_trends(
                base_prediction, 
                property_data['municipality'],
                prediction_horizon
            )
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(
                market_adjusted_prediction,
                historical_data,
                prediction_horizon
            )
            
            # Detect anomalies
            anomalies = self._detect_anomalies(property_data, historical_data)
            
            # Generate Ethiopian compliance insights
            compliance_insights = self._generate_compliance_insights(property_data)
            
            return {
                'current_value': base_prediction,
                'predicted_values': market_adjusted_prediction,
                'confidence_intervals': confidence_intervals,
                'anomalies': anomalies,
                'compliance_insights': compliance_insights,
                'market_factors': self._get_market_factors(property_data['municipality']),
                'prediction_horizon_months': prediction_horizon,
                'model_version': '1.0.0',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in property value prediction: {str(e)}")
            raise
    
    def _get_historical_data(self, db: Session, property_data: Dict) -> List[Dict]:
        """Get historical valuation data for similar properties."""
        try:
            # Query similar properties in the same municipality
            similar_properties = db.query(Property).filter(
                Property.municipality == property_data['municipality'],
                Property.property_type == property_data['property_type']
            ).all()
            
            historical_data = []
            for prop in similar_properties:
                valuations = db.query(Valuation).filter(
                    Valuation.property_id == prop.id
                ).order_by(Valuation.valuation_date.desc()).limit(10).all()
                
                for valuation in valuations:
                    historical_data.append({
                        'property_id': prop.id,
                        'area_sqm': prop.area_sqm,
                        'market_value': valuation.market_value,
                        'valuation_date': valuation.valuation_date,
                        'base_rate': valuation.base_rate
                    })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            return []
    
    def _calculate_base_prediction(self, property_data: Dict, historical_data: List[Dict]) -> float:
        """Calculate base property value prediction."""
        if not historical_data:
            # Fallback to basic calculation
            base_rate = self._get_base_rate(property_data['municipality'])
            area = property_data['area_sqm']
            type_multiplier = self.property_type_weights.get(property_data['property_type'], 1.0)
            
            return base_rate * area * type_multiplier
        
        # Calculate weighted average from historical data
        total_weight = 0
        weighted_value = 0
        
        for data_point in historical_data:
            # Weight by recency and similarity
            recency_weight = self._calculate_recency_weight(data_point['valuation_date'])
            similarity_weight = self._calculate_similarity_weight(property_data, data_point)
            combined_weight = recency_weight * similarity_weight
            
            weighted_value += data_point['market_value'] * combined_weight
            total_weight += combined_weight
        
        if total_weight > 0:
            return weighted_value / total_weight
        else:
            # Fallback to simple average
            return np.mean([d['market_value'] for d in historical_data])
    
    def _apply_market_trends(self, base_value: float, municipality: str, months: int) -> List[float]:
        """Apply market trends to predict future values."""
        factors = self.municipality_factors.get(municipality, {
            'base_multiplier': 1.0,
            'growth_rate': 0.05,
            'demand_factor': 1.0,
            'infrastructure_score': 0.7
        })
        
        predictions = []
        current_value = base_value
        
        for month in range(1, months + 1):
            # Apply compound growth with market factors
            monthly_growth = (factors['growth_rate'] / 12) * factors['demand_factor']
            inflation_adjustment = (self.inflation_rate / 12)
            volatility_factor = 1 + (np.random.normal(0, self.market_volatility) / 12)
            
            growth_multiplier = (1 + monthly_growth + inflation_adjustment) * volatility_factor
            current_value *= growth_multiplier
            
            predictions.append(current_value)
        
        return predictions
    
    def _calculate_confidence_intervals(
        self, 
        predictions: List[float], 
        historical_data: List[Dict], 
        months: int
    ) -> Dict:
        """Calculate confidence intervals for predictions."""
        if len(historical_data) < 3:
            # Default confidence intervals for sparse data
            return {
                'lower_90': [p * 0.7 for p in predictions],
                'upper_90': [p * 1.3 for p in predictions],
                'lower_50': [p * 0.85 for p in predictions],
                'upper_50': [p * 1.15 for p in predictions]
            }
        
        # Calculate historical volatility
        values = [d['market_value'] for d in historical_data]
        volatility = np.std(values) / np.mean(values)
        
        confidence_intervals = {
            'lower_90': [],
            'upper_90': [],
            'lower_50': [],
            'upper_50': []
        }
        
        for i, prediction in enumerate(predictions):
            # Wider confidence intervals for longer predictions
            time_factor = 1 + (i * 0.02)
            
            confidence_intervals['lower_90'].append(prediction * (1 - (1.645 * volatility * time_factor)))
            confidence_intervals['upper_90'].append(prediction * (1 + (1.645 * volatility * time_factor)))
            confidence_intervals['lower_50'].append(prediction * (1 - (0.674 * volatility * time_factor)))
            confidence_intervals['upper_50'].append(prediction * (1 + (0.674 * volatility * time_factor)))
        
        return confidence_intervals
    
    def _detect_anomalies(self, property_data: Dict, historical_data: List[Dict]) -> List[Dict]:
        """Detect anomalies in property data."""
        anomalies = []
        
        if len(historical_data) < 5:
            return anomalies
        
        historical_values = [d['market_value'] for d in historical_data]
        mean_value = np.mean(historical_values)
        std_value = np.std(historical_values)
        
        # Check for price anomalies
        estimated_value = self._calculate_base_prediction(property_data, historical_data)
        z_score = abs(estimated_value - mean_value) / std_value if std_value > 0 else 0
        
        if z_score > 2.5:
            anomalies.append({
                'type': 'price_anomaly',
                'severity': 'high' if z_score > 3.5 else 'medium',
                'description': f'Property value is {z_score:.1f} standard deviations from historical mean',
                'z_score': z_score
            })
        
        # Check for area anomalies
        historical_areas = [d['area_sqm'] for d in historical_data]
        area_mean = np.mean(historical_areas)
        area_std = np.std(historical_areas)
        
        if area_std > 0:
            area_z_score = abs(property_data['area_sqm'] - area_mean) / area_std
            if area_z_score > 2.5:
                anomalies.append({
                    'type': 'area_anomaly',
                    'severity': 'high' if area_z_score > 3.5 else 'medium',
                    'description': f'Property area is {area_z_score:.1f} standard deviations from historical mean',
                    'z_score': area_z_score
                })
        
        return anomalies
    
    def _generate_compliance_insights(self, property_data: Dict) -> Dict:
        """Generate Ethiopian compliance insights."""
        return {
            'proclamation_compliance': '1365/2025',
            'taxable_value_percentage': 25.0,
            'required_documentation': [
                'Land Certificate',
                'Municipality Tax Clearance',
                'Building Permit (if applicable)',
                'Ethiopian ID of Owner'
            ],
            'compliance_checks': {
                'land_registry_verification': 'required',
                'municipal_zoning_compliance': 'required',
                'tax_payment_status': 'required',
                'structural_integrity': 'recommended'
            },
            'regulatory_risks': [
                'Property boundary disputes',
                'Zoning regulation changes',
                'Tax assessment appeals'
            ]
        }
    
    def _get_market_factors(self, municipality: str) -> Dict:
        """Get market factors for a municipality."""
        factors = self.municipality_factors.get(municipality, {
            'base_multiplier': 1.0,
            'growth_rate': 0.05,
            'demand_factor': 1.0,
            'infrastructure_score': 0.7
        })
        
        return {
            'market_temperature': 'hot' if factors['demand_factor'] > 1.1 else 'cold' if factors['demand_factor'] < 0.9 else 'neutral',
            'investment_recommendation': 'buy' if factors['growth_rate'] > 0.07 else 'hold' if factors['growth_rate'] > 0.03 else 'sell',
            'risk_level': 'low' if factors['infrastructure_score'] > 0.8 else 'medium' if factors['infrastructure_score'] > 0.6 else 'high',
            'market_outlook': factors['growth_rate'] * 100
        }
    
    def _get_base_rate(self, municipality: str) -> float:
        """Get base rate for municipality."""
        # Ethiopian municipality base rates (ETB per square meter)
        base_rates = {
            'Addis Ababa': 1000.0,
            'Dire Dawa': 800.0,
            'Mekelle': 600.0,
            'Bahir Dar': 550.0,
            'Adama': 500.0,
            'Hawassa': 450.0,
            'Gonder': 400.0,
            'Jimma': 350.0
        }
        return base_rates.get(municipality, 500.0)
    
    def _calculate_recency_weight(self, valuation_date: datetime) -> float:
        """Calculate weight based on how recent the valuation is."""
        days_ago = (datetime.now() - valuation_date).days
        # Exponential decay: more recent valuations get higher weights
        return np.exp(-days_ago / 365)  # Half-life of 1 year
    
    def _calculate_similarity_weight(self, property_data: Dict, historical_point: Dict) -> float:
        """Calculate weight based on property similarity."""
        area_similarity = 1 - abs(property_data['area_sqm'] - historical_point['area_sqm']) / property_data['area_sqm']
        return max(0.1, area_similarity)  # Minimum weight of 0.1
    
    def analyze_market_trends(self, db: Session, municipality: str = None) -> Dict:
        """Analyze market trends for Ethiopian property market."""
        try:
            # Get market data
            query = db.query(Valuation)
            if municipality:
                # Filter by municipality (would need to join with Property table)
                pass
            
            valuations = query.order_by(Valuation.valuation_date.desc()).limit(1000).all()
            
            if not valuations:
                return {'error': 'Insufficient data for market analysis'}
            
            # Calculate trend metrics
            values = [v.market_value for v in valuations]
            dates = [v.valuation_date for v in valuations]
            
            # Monthly trend analysis
            monthly_data = self._group_by_month(valuations)
            
            # Calculate price trends
            price_trends = self._calculate_price_trends(monthly_data)
            
            # Market volatility
            volatility = np.std(values) / np.mean(values) if values else 0
            
            # Growth rate
            if len(monthly_data) > 1:
                growth_rate = self._calculate_growth_rate(monthly_data)
            else:
                growth_rate = 0
            
            return {
                'current_market_state': {
                    'average_value': np.mean(values),
                    'median_value': np.median(values),
                    'volatility': volatility,
                    'trend_direction': 'increasing' if growth_rate > 0 else 'decreasing' if growth_rate < 0 else 'stable',
                    'growth_rate': growth_rate
                },
                'monthly_trends': price_trends,
                'market_indicators': {
                    'price_momentum': growth_rate * 12,  # Annualized
                    'market_efficiency': 1 - volatility,  # Higher efficiency = lower volatility
                    'liquidity_score': len(valuations) / 100  # Normalized liquidity
                },
                'ethiopian_factors': {
                    'inflation_impact': self.inflation_rate,
                    'urbanization_impact': self.urban_growth_rate,
                    'regulatory_stability': 0.8  # Assumed stability score
                },
                'recommendations': self._generate_market_recommendations(growth_rate, volatility)
            }
            
        except Exception as e:
            logger.error(f"Error in market trends analysis: {str(e)}")
            return {'error': str(e)}
    
    def _group_by_month(self, valuations: List[Valuation]) -> Dict:
        """Group valuations by month."""
        monthly_data = {}
        for valuation in valuations:
            month_key = valuation.valuation_date.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = []
            monthly_data[month_key].append(valuation.market_value)
        
        # Calculate monthly averages
        return {month: np.mean(values) for month, values in monthly_data.items()}
    
    def _calculate_price_trends(self, monthly_data: Dict) -> List[Dict]:
        """Calculate price trends from monthly data."""
        sorted_months = sorted(monthly_data.keys())
        trends = []
        
        for i, month in enumerate(sorted_months):
            if i == 0:
                change_pct = 0
            else:
                prev_month = sorted_months[i-1]
                change_pct = ((monthly_data[month] - monthly_data[prev_month]) / monthly_data[prev_month]) * 100
            
            trends.append({
                'month': month,
                'average_value': monthly_data[month],
                'change_percentage': change_pct
            })
        
        return trends
    
    def _calculate_growth_rate(self, monthly_data: Dict) -> float:
        """Calculate compound monthly growth rate."""
        months = sorted(monthly_data.keys())
        if len(months) < 2:
            return 0
        
        first_value = monthly_data[months[0]]
        last_value = monthly_data[months[-1]]
        periods = len(months) - 1
        
        if first_value <= 0:
            return 0
        
        return (last_value / first_value) ** (1 / periods) - 1
    
    def _generate_market_recommendations(self, growth_rate: float, volatility: float) -> List[str]:
        """Generate market recommendations based on analysis."""
        recommendations = []
        
        if growth_rate > 0.05:  # 5% monthly growth
            recommendations.append("Strong market growth - favorable for investment")
        elif growth_rate < -0.02:  # -2% monthly growth
            recommendations.append("Market declining - exercise caution with new investments")
        else:
            recommendations.append("Stable market - moderate investment opportunity")
        
        if volatility > 0.2:
            recommendations.append("High volatility - consider risk mitigation strategies")
        elif volatility < 0.1:
            recommendations.append("Low volatility - stable market conditions")
        
        # Ethiopian-specific recommendations
        recommendations.append("Monitor Proclamation 1365/2025 compliance requirements")
        recommendations.append("Consider urban development plans in major municipalities")
        
        return recommendations

# Global ML service instance
ml_service = EthiopianPropertyMLService()
