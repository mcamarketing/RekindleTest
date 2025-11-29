"""
ARE Revenue Forecaster Service Wrapper

Provides predictive analytics and revenue forecasting using historical data,
market trends, and ML-driven insights.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics
import math

logger = logging.getLogger(__name__)

class ForecastPeriod(Enum):
    """Forecast time periods"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"

class ForecastType(Enum):
    """Types of forecasts"""
    CONSERVATIVE = "conservative"
    REALISTIC = "realistic"
    OPTIMISTIC = "optimistic"
    AGGRESSIVE = "aggressive"

class ConfidenceInterval(Enum):
    """Confidence levels for forecasts"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class RevenueForecast:
    """Represents a revenue forecast"""
    forecast_id: str
    period: ForecastPeriod
    forecast_type: ForecastType
    start_date: datetime
    end_date: datetime
    predicted_revenue: float
    confidence_interval: ConfidenceInterval
    confidence_range: Dict[str, float]  # min, max, mean
    drivers: Dict[str, float]  # factors influencing forecast
    assumptions: List[str]
    risk_factors: List[str]
    generated_at: datetime
    historical_accuracy: Optional[float] = None

@dataclass
class ForecastScenario:
    """Represents a forecast scenario analysis"""
    scenario_id: str
    name: str
    description: str
    forecasts: Dict[str, RevenueForecast]  # forecast_type -> forecast
    comparison_metrics: Dict[str, Any]
    recommended_scenario: str
    created_at: datetime

class RevenueForecasterAgent:
    """ARE Revenue Forecaster - Predictive revenue analytics"""

    def __init__(self):
        self.forecasts: Dict[str, RevenueForecast] = {}
        self.scenarios: Dict[str, ForecastScenario] = {}
        self.historical_data: List[Dict[str, Any]] = []
        self.forecast_accuracy_history: List[float] = []

        # Forecasting parameters
        self.default_conversion_rates = {
            "lead_to_mql": 0.15,
            "mql_to_sql": 0.25,
            "sql_to_closed": 0.35
        }
        self.seasonal_factors = self._initialize_seasonal_factors()

    def _initialize_seasonal_factors(self) -> Dict[str, float]:
        """Initialize seasonal adjustment factors"""
        return {
            "jan": 0.8, "feb": 0.9, "mar": 1.2, "apr": 1.1, "may": 1.0, "jun": 1.0,
            "jul": 0.9, "aug": 0.8, "sep": 1.1, "oct": 1.3, "nov": 1.4, "dec": 1.5
        }

    async def run(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Main execution method"""
        action = input_data.get('action', 'forecast')

        logger.info(f"Revenue Forecaster Agent executing action: {action}")

        try:
            if action == 'generate_forecast':
                return await self._generate_forecast(input_data)
            elif action == 'create_scenario':
                return await self._create_scenario(input_data)
            elif action == 'analyze_trends':
                return await self._analyze_trends(input_data)
            elif action == 'validate_forecast':
                return await self._validate_forecast(input_data)
            elif action == 'get_forecast_insights':
                return self._get_forecast_insights()
            else:
                raise ValueError(f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"Revenue Forecaster execution failed: {e}")
            raise

    async def _generate_forecast(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate revenue forecast"""
        period = ForecastPeriod(input_data.get('period', 'monthly').upper())
        forecast_type = ForecastType(input_data.get('forecast_type', 'realistic').upper())
        historical_data = input_data.get('historical_data', [])
        current_pipeline = input_data.get('current_pipeline', {})
        market_factors = input_data.get('market_factors', {})

        # Store historical data for future reference
        self.historical_data.extend(historical_data)

        # Calculate forecast
        forecast_result = await self._calculate_forecast(
            period, forecast_type, historical_data, current_pipeline, market_factors
        )

        forecast = RevenueForecast(
            forecast_id=f"forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            period=period,
            forecast_type=forecast_type,
            start_date=datetime.now(),
            end_date=self._calculate_end_date(period),
            predicted_revenue=forecast_result['predicted_revenue'],
            confidence_interval=forecast_result['confidence_interval'],
            confidence_range=forecast_result['confidence_range'],
            drivers=forecast_result['drivers'],
            assumptions=forecast_result['assumptions'],
            risk_factors=forecast_result['risk_factors'],
            generated_at=datetime.now(),
            historical_accuracy=self._calculate_historical_accuracy()
        )

        self.forecasts[forecast.forecast_id] = forecast

        logger.info(f"Generated {forecast_type.value} {period.value} forecast: £{forecast.predicted_revenue:,.0f}")

        return {
            "status": "generated",
            "forecast_id": forecast.forecast_id,
            "predicted_revenue": forecast.predicted_revenue,
            "confidence_range": forecast.confidence_range,
            "key_drivers": list(forecast.drivers.keys())[:5],
            "risk_factors": forecast.risk_factors[:3]
        }

    async def _create_scenario(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create forecast scenario analysis"""
        scenario_name = input_data.get('name', 'Revenue Scenario Analysis')
        description = input_data.get('description', '')
        base_data = input_data.get('base_data', {})
        scenario_variables = input_data.get('scenario_variables', {})

        # Generate multiple forecast scenarios
        scenarios = {}
        comparison_metrics = {}

        for forecast_type in ForecastType:
            forecast_input = base_data.copy()
            forecast_input.update(scenario_variables.get(forecast_type.value, {}))
            forecast_input['forecast_type'] = forecast_type.value

            forecast_result = await self._generate_forecast(forecast_input)
            if forecast_result['status'] == 'generated':
                scenarios[forecast_type.value] = self.forecasts[forecast_result['forecast_id']]

        # Calculate comparison metrics
        if scenarios:
            revenues = [f.predicted_revenue for f in scenarios.values()]
            comparison_metrics = {
                "range": max(revenues) - min(revenues),
                "average": sum(revenues) / len(revenues),
                "best_case": max(revenues),
                "worst_case": min(revenues),
                "most_likely": scenarios.get('realistic', scenarios.get('moderate', list(scenarios.values())[0])).predicted_revenue
            }

        # Determine recommended scenario
        recommended = self._determine_recommended_scenario(scenarios)

        scenario = ForecastScenario(
            scenario_id=f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=scenario_name,
            description=description,
            forecasts=scenarios,
            comparison_metrics=comparison_metrics,
            recommended_scenario=recommended,
            created_at=datetime.now()
        )

        self.scenarios[scenario.scenario_id] = scenario

        logger.info(f"Created forecast scenario: {scenario_name} with {len(scenarios)} forecasts")

        return {
            "status": "created",
            "scenario_id": scenario.scenario_id,
            "forecast_count": len(scenarios),
            "recommended_scenario": recommended,
            "revenue_range": comparison_metrics.get("range", 0)
        }

    async def _analyze_trends(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze revenue trends and patterns"""
        time_period = input_data.get('time_period', 'last_12_months')
        metrics_to_analyze = input_data.get('metrics', ['revenue', 'conversion_rate', 'deal_size'])

        # Extract trend data
        trend_data = await self._extract_trend_data(time_period, metrics_to_analyze)

        # Analyze patterns
        patterns = await self._analyze_patterns(trend_data)

        # Generate insights
        insights = await self._generate_trend_insights(patterns)

        return {
            "status": "analyzed",
            "time_period": time_period,
            "patterns_detected": len(patterns),
            "key_insights": insights,
            "trend_direction": patterns.get('overall_trend', 'stable'),
            "confidence_score": patterns.get('confidence', 0.5)
        }

    async def _validate_forecast(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate forecast accuracy against actual results"""
        forecast_id = input_data.get('forecast_id')
        actual_results = input_data.get('actual_results', {})

        if not forecast_id or forecast_id not in self.forecasts:
            raise ValueError("Valid forecast_id is required")

        forecast = self.forecasts[forecast_id]

        # Calculate accuracy metrics
        accuracy_metrics = self._calculate_forecast_accuracy(forecast, actual_results)

        # Update forecast with accuracy
        forecast.historical_accuracy = accuracy_metrics['accuracy_score']

        # Store accuracy for future reference
        self.forecast_accuracy_history.append(accuracy_metrics['accuracy_score'])

        logger.info(f"Validated forecast {forecast_id}: {accuracy_metrics['accuracy_score']:.2%} accuracy")

        return {
            "status": "validated",
            "forecast_id": forecast_id,
            "accuracy_score": accuracy_metrics['accuracy_score'],
            "error_metrics": accuracy_metrics,
            "improvement_suggestions": accuracy_metrics.get('suggestions', [])
        }

    def _get_forecast_insights(self) -> Dict[str, Any]:
        """Get aggregated forecast insights"""
        total_forecasts = len(self.forecasts)

        if total_forecasts == 0:
            return {"status": "no_forecasts"}

        # Calculate aggregate metrics
        recent_forecasts = [
            f for f in self.forecasts.values()
            if (datetime.now() - f.generated_at).days <= 30
        ]

        if recent_forecasts:
            avg_predicted_revenue = sum(f.predicted_revenue for f in recent_forecasts) / len(recent_forecasts)
            avg_confidence = sum(
                {'low': 0.3, 'medium': 0.6, 'high': 0.9}[f.confidence_interval.value]
                for f in recent_forecasts
            ) / len(recent_forecasts)
        else:
            avg_predicted_revenue = 0
            avg_confidence = 0

        # Forecast accuracy
        if self.forecast_accuracy_history:
            avg_accuracy = sum(self.forecast_accuracy_history) / len(self.forecast_accuracy_history)
        else:
            avg_accuracy = None

        # Distribution by type and period
        by_type = {}
        by_period = {}
        for f in recent_forecasts:
            # By type
            f_type = f.forecast_type.value
            if f_type not in by_type:
                by_type[f_type] = {"count": 0, "total_revenue": 0}
            by_type[f_type]["count"] += 1
            by_type[f_type]["total_revenue"] += f.predicted_revenue

            # By period
            f_period = f.period.value
            if f_period not in by_period:
                by_period[f_period] = 0
            by_period[f_period] += 1

        return {
            "status": "insights_generated",
            "total_forecasts": total_forecasts,
            "recent_forecasts": len(recent_forecasts),
            "average_predicted_revenue": avg_predicted_revenue,
            "average_confidence": avg_confidence,
            "average_accuracy": avg_accuracy,
            "distribution_by_type": by_type,
            "distribution_by_period": by_period,
            "most_common_type": max(by_type.items(), key=lambda x: x[1]["count"])[0] if by_type else None,
            "generated_at": datetime.now().isoformat()
        }

    async def _calculate_forecast(self, period: ForecastPeriod, forecast_type: ForecastType,
                                historical_data: List[Dict[str, Any]], current_pipeline: Dict[str, Any],
                                market_factors: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate revenue forecast"""
        # Extract historical metrics
        historical_revenue = [d.get('revenue', 0) for d in historical_data]
        historical_conversion = [d.get('conversion_rate', 0.1) for d in historical_data]

        # Calculate base metrics
        avg_revenue = statistics.mean(historical_revenue) if historical_revenue else 0
        avg_conversion = statistics.mean(historical_conversion) if historical_conversion else 0.1

        # Apply forecast type adjustments
        type_multipliers = {
            ForecastType.CONSERVATIVE: 0.8,
            ForecastType.REALISTIC: 1.0,
            ForecastType.OPTIMISTIC: 1.3,
            ForecastType.AGGRESSIVE: 1.6
        }

        base_multiplier = type_multipliers[forecast_type]

        # Apply period adjustments
        period_multipliers = {
            ForecastPeriod.MONTHLY: 1.0,
            ForecastPeriod.QUARTERLY: 3.0,
            ForecastPeriod.ANNUAL: 12.0
        }

        period_multiplier = period_multipliers[period]

        # Calculate pipeline contribution
        pipeline_value = current_pipeline.get('total_value', 0)
        pipeline_probability = current_pipeline.get('weighted_probability', 0.3)
        pipeline_contribution = pipeline_value * pipeline_probability

        # Apply market factors
        market_multiplier = 1.0
        for factor, impact in market_factors.items():
            market_multiplier *= (1 + impact)

        # Calculate seasonal adjustment
        seasonal_adjustment = self._calculate_seasonal_adjustment(period)

        # Calculate final forecast
        historical_base = avg_revenue * base_multiplier * period_multiplier
        pipeline_adjusted = historical_base + pipeline_contribution
        market_adjusted = pipeline_adjusted * market_multiplier
        final_forecast = market_adjusted * seasonal_adjustment

        # Calculate confidence range
        confidence_range = self._calculate_confidence_range(final_forecast, forecast_type)

        # Determine confidence interval
        confidence_interval = self._determine_confidence_interval(forecast_type, len(historical_data))

        # Identify key drivers
        drivers = {
            "historical_performance": historical_base / final_forecast,
            "pipeline_contribution": pipeline_contribution / final_forecast,
            "market_factors": market_multiplier - 1.0,
            "seasonal_adjustment": seasonal_adjustment - 1.0
        }

        # Generate assumptions and risk factors
        assumptions = await self._generate_assumptions(forecast_type, period, market_factors)
        risk_factors = await self._generate_risk_factors(forecast_type, market_factors)

        return {
            "predicted_revenue": final_forecast,
            "confidence_interval": confidence_interval,
            "confidence_range": confidence_range,
            "drivers": drivers,
            "assumptions": assumptions,
            "risk_factors": risk_factors
        }

    def _calculate_end_date(self, period: ForecastPeriod) -> datetime:
        """Calculate forecast end date"""
        now = datetime.now()

        if period == ForecastPeriod.MONTHLY:
            return now + timedelta(days=30)
        elif period == ForecastPeriod.QUARTERLY:
            return now + timedelta(days=90)
        elif period == ForecastPeriod.ANNUAL:
            return now + timedelta(days=365)

        return now + timedelta(days=30)

    def _calculate_seasonal_adjustment(self, period: ForecastPeriod) -> float:
        """Calculate seasonal adjustment factor"""
        if period == ForecastPeriod.MONTHLY:
            current_month = datetime.now().strftime('%b').lower()
            return self.seasonal_factors.get(current_month, 1.0)
        else:
            # For longer periods, use average seasonal factor
            return sum(self.seasonal_factors.values()) / len(self.seasonal_factors)

    def _calculate_confidence_range(self, forecast: float, forecast_type: ForecastType) -> Dict[str, float]:
        """Calculate confidence range for forecast"""
        # Base variance based on forecast type
        variance_multipliers = {
            ForecastType.CONSERVATIVE: 0.1,  # ±10%
            ForecastType.REALISTIC: 0.15,    # ±15%
            ForecastType.OPTIMISTIC: 0.25,   # ±25%
            ForecastType.AGGRESSIVE: 0.4     # ±40%
        }

        variance = variance_multipliers[forecast_type]
        range_amount = forecast * variance

        return {
            "min": max(0, forecast - range_amount),
            "max": forecast + range_amount,
            "mean": forecast,
            "range": range_amount * 2
        }

    def _determine_confidence_interval(self, forecast_type: ForecastType, data_points: int) -> ConfidenceInterval:
        """Determine confidence interval based on forecast type and data quality"""
        # Base confidence on data quality
        if data_points < 3:
            base_confidence = ConfidenceInterval.LOW
        elif data_points < 12:
            base_confidence = ConfidenceInterval.MEDIUM
        else:
            base_confidence = ConfidenceInterval.HIGH

        # Adjust based on forecast type
        if forecast_type in [ForecastType.CONSERVATIVE, ForecastType.REALISTIC]:
            return base_confidence
        else:
            # Optimistic/aggressive forecasts have lower confidence
            if base_confidence == ConfidenceInterval.HIGH:
                return ConfidenceInterval.MEDIUM
            else:
                return ConfidenceInterval.LOW

    async def _generate_assumptions(self, forecast_type: ForecastType, period: ForecastPeriod,
                                  market_factors: Dict[str, Any]) -> List[str]:
        """Generate forecast assumptions"""
        assumptions = [
            f"Forecast based on {forecast_type.value} growth assumptions",
            f"Conversion rates remain consistent with historical averages",
            f"Market conditions remain stable over {period.value} period"
        ]

        if market_factors:
            assumptions.append("Market factor impacts applied as specified")

        if period == ForecastPeriod.ANNUAL:
            assumptions.append("Seasonal patterns normalized across full year")

        return assumptions

    async def _generate_risk_factors(self, forecast_type: ForecastType,
                                   market_factors: Dict[str, Any]) -> List[str]:
        """Generate forecast risk factors"""
        risk_factors = []

        if forecast_type == ForecastType.AGGRESSIVE:
            risk_factors.append("High growth assumptions increase forecast uncertainty")

        if not market_factors:
            risk_factors.append("Market factors not specified - forecast may be optimistic")

        risk_factors.extend([
            "Economic conditions may impact conversion rates",
            "Competitor actions could affect market share",
            "Seasonal variations may deviate from historical patterns"
        ])

        return risk_factors

    def _determine_recommended_scenario(self, scenarios: Dict[str, RevenueForecast]) -> str:
        """Determine recommended forecast scenario"""
        if not scenarios:
            return "realistic"

        # Prefer realistic scenario if available
        if 'realistic' in scenarios:
            return 'realistic'

        # Otherwise, choose based on confidence
        best_scenario = max(scenarios.items(),
                          key=lambda x: {'low': 0.3, 'medium': 0.6, 'high': 0.9}[x[1].confidence_interval.value])

        return best_scenario[0]

    async def _extract_trend_data(self, time_period: str, metrics: List[str]) -> Dict[str, Any]:
        """Extract trend data for analysis"""
        # Parse time period
        if time_period == 'last_12_months':
            months_back = 12
        elif time_period == 'last_6_months':
            months_back = 6
        else:
            months_back = 3

        cutoff_date = datetime.now() - timedelta(days=months_back * 30)

        # Filter historical data
        relevant_data = [
            d for d in self.historical_data
            if d.get('date') and datetime.fromisoformat(d['date']) >= cutoff_date
        ]

        trend_data = {}
        for metric in metrics:
            values = [d.get(metric, 0) for d in relevant_data if metric in d]
            if values:
                trend_data[metric] = {
                    "values": values,
                    "average": statistics.mean(values),
                    "trend": self._calculate_trend(values),
                    "volatility": self._calculate_volatility(values)
                }

        return trend_data

    async def _analyze_patterns(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in trend data"""
        patterns = {
            "overall_trend": "stable",
            "confidence": 0.5,
            "key_patterns": [],
            "anomalies": []
        }

        if not trend_data:
            return patterns

        # Analyze overall trend
        revenue_trend = trend_data.get('revenue', {}).get('trend', 0)
        if revenue_trend > 0.1:
            patterns["overall_trend"] = "increasing"
            patterns["confidence"] = 0.8
        elif revenue_trend < -0.1:
            patterns["overall_trend"] = "decreasing"
            patterns["confidence"] = 0.8
        else:
            patterns["overall_trend"] = "stable"
            patterns["confidence"] = 0.6

        # Detect seasonality
        if 'revenue' in trend_data:
            seasonal_pattern = self._detect_seasonality(trend_data['revenue']['values'])
            if seasonal_pattern:
                patterns["key_patterns"].append("seasonal_pattern_detected")

        # Detect anomalies
        for metric, data in trend_data.items():
            anomalies = self._detect_anomalies(data['values'])
            if anomalies:
                patterns["anomalies"].extend([f"{metric}: {anomaly}" for anomaly in anomalies])

        return patterns

    async def _generate_trend_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate insights from trend analysis"""
        insights = []

        trend = patterns.get('overall_trend', 'stable')
        if trend == 'increasing':
            insights.append("Revenue showing positive growth trend")
        elif trend == 'decreasing':
            insights.append("Revenue declining - investigate underlying causes")
        else:
            insights.append("Revenue stable with normal fluctuations")

        if 'seasonal_pattern_detected' in patterns.get('key_patterns', []):
            insights.append("Seasonal patterns detected - consider timing optimizations")

        anomalies = patterns.get('anomalies', [])
        if anomalies:
            insights.append(f"Detected {len(anomalies)} anomalous data points requiring investigation")

        confidence = patterns.get('confidence', 0.5)
        if confidence > 0.8:
            insights.append("High confidence in trend analysis")
        elif confidence < 0.6:
            insights.append("Trend analysis has low confidence - more data recommended")

        return insights

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend slope"""
        if len(values) < 2:
            return 0.0

        x = list(range(len(values)))
        try:
            slope = statistics.linear_regression(x, values)[0]
            # Normalize by average value
            avg_value = statistics.mean(values)
            return slope / avg_value if avg_value != 0 else 0
        except:
            return 0.0

    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (coefficient of variation)"""
        if len(values) < 2:
            return 0.0

        try:
            mean = statistics.mean(values)
            std_dev = statistics.stdev(values)
            return std_dev / mean if mean != 0 else 0
        except:
            return 0.0

    def _detect_seasonality(self, values: List[float]) -> bool:
        """Simple seasonality detection"""
        if len(values) < 12:
            return False

        # Check for repeating patterns (simplified)
        # In production, use proper seasonal decomposition
        return len(values) >= 12  # Placeholder

    def _detect_anomalies(self, values: List[float]) -> List[str]:
        """Detect anomalous values"""
        if len(values) < 3:
            return []

        anomalies = []
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0

        if std_dev == 0:
            return []

        for i, value in enumerate(values):
            z_score = abs(value - mean) / std_dev
            if z_score > 2.5:  # 2.5 standard deviations
                anomalies.append(f"point_{i}: {value:.2f} (z={z_score:.1f})")

        return anomalies

    def _calculate_forecast_accuracy(self, forecast: RevenueForecast,
                                   actual_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate forecast accuracy metrics"""
        actual_revenue = actual_results.get('actual_revenue', 0)
        predicted = forecast.predicted_revenue

        if actual_revenue == 0 and predicted == 0:
            accuracy_score = 1.0
        elif actual_revenue == 0 or predicted == 0:
            accuracy_score = 0.0
        else:
            accuracy_score = 1 - abs(predicted - actual_revenue) / max(predicted, actual_revenue)

        error_metrics = {
            "accuracy_score": accuracy_score,
            "absolute_error": abs(predicted - actual_revenue),
            "percentage_error": abs(predicted - actual_revenue) / actual_revenue if actual_revenue != 0 else float('inf'),
            "forecast_bias": predicted - actual_revenue
        }

        # Generate improvement suggestions
        suggestions = []
        if accuracy_score < 0.7:
            suggestions.append("Consider adjusting forecast assumptions")
        if abs(error_metrics["forecast_bias"]) > predicted * 0.2:
            suggestions.append("Review bias in forecasting methodology")

        error_metrics["suggestions"] = suggestions

        return error_metrics

    def _calculate_historical_accuracy(self) -> Optional[float]:
        """Calculate average historical accuracy"""
        if not self.forecast_accuracy_history:
            return None

        return sum(self.forecast_accuracy_history) / len(self.forecast_accuracy_history)