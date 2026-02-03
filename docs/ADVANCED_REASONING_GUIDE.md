# Advanced Reasoning Agent - Guía Completa

## 🧠 Descripción

El `AdvancedReasoningAgent` es la implementación TOP 1% que maximiza la transparencia, reduce sesgos y cuantifica incertidumbre en análisis estratégicos.

**Características únicas que nos diferencian:**

- ✅ **Visible Chain-of-Thought** - El usuario VE el razonamiento paso a paso
- ✅ **Multi-Agent Debate** - Múltiples perspectivas reducen sesgo
- ✅ **Uncertainty Quantification** - Honesto sobre limitaciones
- ✅ **Data Quality Assessment** - Consciente de GIGO (Garbage In, Garbage Out)
- ✅ **Audience-Targeted Summaries** - Comunicación adaptada al público

---

## 🎯 Por Qué Esto Es TOP 1%

### Problema con Agentes Tradicionales

```python
# ❌ Agente tradicional (caja negra)
result = agent.analyze_bcg(data)
# Usuario recibe: "Tacos al Pastor es un Star"
# Usuario NO sabe: ¿Por qué? ¿Qué tan seguro? ¿Qué asumió?
```

### Nuestra Solución

```python
# ✅ Advanced Reasoning Agent (transparente)
result = await agent.analyse_bcg_strategy(
    sales_data=data,
    enable_multi_perspective=True,
    show_reasoning=True
)

# Usuario recibe:
# - Razonamiento paso a paso visible
# - Confidence scores por categoría
# - Asunciones hechas explícitas
# - Interpretaciones alternativas
# - Limitaciones reconocidas
# - Debate entre 3 perspectivas expertas
```

---

## 🚀 Uso Básico

### Inicialización

```python
from app.services.gemini.advanced_reasoning import AdvancedReasoningAgent

# Inicializar agente
agent = AdvancedReasoningAgent()
```

---

## 📊 Análisis BCG con Razonamiento Visible

### Análisis Completo

```python
# Datos de ventas
sales_data = [
    {
        "product_name": "Tacos al Pastor",
        "units_sold": 450,
        "price": 45.0,
        "cost": 18.0,
        "date": "2026-01-15"
    },
    # ... más productos
]

# Datos de menú
menu_data = [
    {
        "name": "Tacos al Pastor",
        "category": "Tacos",
        "description": "Con piña y cilantro"
    },
    # ... más items
]

# Contexto de mercado (opcional)
market_context = {
    "market_size": "growing",
    "competition_level": "high",
    "customer_segment": "millennials"
}

# Análisis BCG completo
analysis = await agent.analyse_bcg_strategy(
    sales_data=sales_data,
    menu_data=menu_data,
    market_context=market_context,
    enable_multi_perspective=True,  # Debate multi-agente
    show_reasoning=True  # Mostrar razonamiento
)

# Ver resultados estructurados
print(f"Overall confidence: {analysis.overall_confidence}")
print(f"Data quality: {analysis.data_quality_assessment.overall_quality}")

# Ver clasificación de productos
for product in analysis.products:
    print(f"\n{product.product_name}:")
    print(f"  Category: {product.category}")
    print(f"  Confidence: {product.confidence}")
    print(f"  Reasoning: {product.reasoning}")
    
    if product.alternative_classification:
        print(f"  Alternative: {product.alternative_classification}")
        print(f"  Why: {product.alternative_reasoning}")
```

### Ver Razonamiento Paso a Paso

```python
# El razonamiento visible es clave para transparencia
print("\n🧠 REASONING CHAIN:")
for i, step in enumerate(analysis.reasoning_chain, 1):
    print(f"{i}. {step}")

# Ejemplo de output:
# 1. Calculated market growth rate: 15% (based on 3-month trend)
# 2. Determined market leader: Competitor A with 35% share
# 3. Classified Tacos al Pastor as Star (high growth, high share)
# 4. Confidence reduced to 0.75 due to limited market data
# 5. Alternative interpretation: Could be Question Mark if market share calculation is off
```

### Ver Asunciones y Limitaciones

```python
# Asunciones hechas
print("\n📋 ASSUMPTIONS MADE:")
for assumption in analysis.assumptions_made:
    print(f"  - {assumption}")

# Limitaciones reconocidas
print("\n⚠️ LIMITATIONS:")
for limitation in analysis.limitations:
    print(f"  - {limitation}")

# Interpretaciones alternativas
print("\n🔄 ALTERNATIVE INTERPRETATIONS:")
for alt in analysis.alternative_interpretations:
    print(f"  - {alt}")
```

---

## 🔥 Multi-Agent Debate (Reducir Sesgo)

### ¿Por Qué Multi-Agent Debate?

**Problema:** Un solo agente puede tener sesgos implícitos.

**Solución:** Simular múltiples expertos con diferentes perspectivas:
- **Aggressive Growth Strategist** - Favorece inversión agresiva
- **Conservative CFO** - Favorece estabilidad financiera
- **Customer-Centric CMO** - Favorece satisfacción del cliente

### Análisis con Debate

```python
# Habilitar multi-perspective
analysis = await agent.analyse_bcg_strategy(
    sales_data=sales_data,
    menu_data=menu_data,
    enable_multi_perspective=True  # ⭐ Clave
)

# Ver recomendaciones estratégicas con consenso
for category, recommendation in analysis.strategic_recommendations.items():
    print(f"\n{category.upper()}:")
    print(f"  Consensus: {recommendation.consensus_level}")
    print(f"  Confidence: {recommendation.confidence}")
    
    print("  Recommendations:")
    for rec in recommendation.recommendations:
        print(f"    - {rec}")
    
    if recommendation.alternative_views:
        print("  Alternative views:")
        for alt in recommendation.alternative_views:
            print(f"    - {alt}")
    
    print("  Risks:")
    for risk in recommendation.risks:
        print(f"    - {risk}")
```

### Ejemplo de Output

```
STARS:
  Consensus: strong (75%+ agreement)
  Confidence: 0.85
  Recommendations:
    - Increase marketing budget by 30% for Tacos al Pastor
    - Expand to 3 new locations in high-traffic areas
    - Develop premium variant with imported ingredients
  Alternative views:
    - CFO perspective: Reduce investment, focus on margin optimization
  Risks:
    - Market saturation in 12-18 months
    - Competitor response could erode margins
```

---

## 📈 Evaluación de Calidad de Datos

### Antes del Análisis

```python
# El agente automáticamente evalúa calidad de datos
analysis = await agent.analyse_bcg_strategy(sales_data, menu_data)

# Ver evaluación de calidad
quality = analysis.data_quality_assessment

print(f"Completeness: {quality.completeness:.2f}")
print(f"Consistency: {quality.consistency:.2f}")
print(f"Recency: {quality.recency:.2f}")
print(f"Sample size: {quality.sample_size_adequacy:.2f}")
print(f"Overall quality: {quality.overall_quality:.2f}")

# Ver problemas específicos
if quality.missing_fields:
    print("\n⚠️ Missing fields:")
    for field in quality.missing_fields:
        print(f"  - {field}")

if quality.quality_issues:
    print("\n⚠️ Quality issues:")
    for issue in quality.quality_issues:
        print(f"  - {issue}")

# Ver recomendaciones de mejora
print("\n💡 Recommendations to improve data:")
for rec in quality.improvement_recommendations:
    print(f"  - {rec}")
```

### Impacto en Confidence

```python
# La calidad de datos afecta la confianza
if quality.overall_quality < 0.6:
    print("⚠️ LOW DATA QUALITY - Results have high uncertainty")
    print(f"Overall confidence reduced to: {analysis.overall_confidence}")
```

---

## 📝 Executive Summaries (Audience-Targeted)

### Para Dueño de Restaurante

```python
# Resumen para dueño (no técnico, orientado a acción)
summary = await agent.generate_executive_summary(
    full_analysis=analysis.model_dump(),
    audience="restaurant_owner",
    max_words=300
)

print(summary)
```

**Ejemplo de output:**

```
Your menu has 3 clear winners and 2 products losing money.

KEY FINDING: Tacos al Pastor is your star performer - high sales, 
high profit margin. It's driving 40% of your revenue.

RECOMMENDATION: Double down on your winners. Increase Tacos al Pastor 
marketing by 30%, consider raising price by $5 (customers will pay it), 
and stop promoting the Burrito Grande - it's losing $200/week.

EXPECTED IMPACT: +25% profit in 3 months if you focus resources on 
top 3 products.

NEXT STEPS:
- This week: Stop burrito promotions, reallocate budget to tacos
- Next week: Test $50 price point for Tacos al Pastor
- This month: Train staff to upsell top performers
```

### Para Inversionista

```python
# Resumen para inversionista (métricas financieras, ROI)
summary = await agent.generate_executive_summary(
    full_analysis=analysis.model_dump(),
    audience="investor",
    max_words=300
)
```

**Ejemplo de output:**

```
Portfolio analysis reveals 60% revenue concentration in 3 SKUs 
with 45% gross margin.

KEY FINDING: Strong product-market fit in premium taco segment. 
Market growing 15% YoY, we're capturing 22% share vs 18% industry average.

RECOMMENDATION: Accelerate growth investment. Stars category (40% of revenue) 
shows 3x ROI on marketing spend. Question Marks need $50K investment or 
discontinuation decision within 60 days.

EXPECTED IMPACT: Path to 30% revenue growth, 50% margin expansion through 
portfolio optimization.

NEXT STEPS:
- Secure $150K growth capital for market expansion
- Divest underperforming SKUs (20% of portfolio, -5% margin drag)
- Scale Stars category to 60% of revenue within 12 months
```

### Para Consultor

```python
# Resumen para consultor (metodología, rigor analítico)
summary = await agent.generate_executive_summary(
    full_analysis=analysis.model_dump(),
    audience="consultant",
    max_words=300
)
```

### Para Operations Manager

```python
# Resumen para gerente de operaciones (táctico, implementable)
summary = await agent.generate_executive_summary(
    full_analysis=analysis.model_dump(),
    audience="operations_manager",
    max_words=300
)
```

---

## 🎯 Análisis Competitivo

### Posicionamiento vs Competencia

```python
# Tus datos
your_data = {
    "name": "Mi Restaurante",
    "avg_price": 75.0,
    "rating": 4.5,
    "review_count": 450,
    "specialties": ["Tacos", "Burritos"]
}

# Datos de competidores
competitor_data = [
    {
        "name": "Competidor A",
        "avg_price": 85.0,
        "rating": 4.7,
        "review_count": 890
    },
    {
        "name": "Competidor B",
        "avg_price": 60.0,
        "rating": 4.2,
        "review_count": 320
    }
]

# Análisis competitivo
competitive_analysis = await agent.analyse_competitive_position(
    your_data=your_data,
    competitor_data=competitor_data,
    market_context=market_context
)

# Ver posicionamiento
print(f"Your rank: {competitive_analysis['rank']}")
print(f"Confidence: {competitive_analysis['confidence']}")

print("\nStrengths:")
for strength in competitive_analysis['strengths']:
    print(f"  ✅ {strength}")

print("\nWeaknesses:")
for weakness in competitive_analysis['weaknesses']:
    print(f"  ❌ {weakness}")

print("\nStrategic recommendations:")
for rec in competitive_analysis['recommendations']:
    print(f"  💡 {rec}")
```

---

## 📊 Schemas de Respuesta

### BCGAnalysisSchema

```python
{
    "products": [
        {
            "product_name": "Tacos al Pastor",
            "category": "star",
            "growth_rate": 15.5,
            "relative_market_share": 1.8,
            "confidence": 0.85,
            "reasoning": "High growth market (15%), strong relative share (1.8x leader)",
            "assumptions": [
                "Market leader is Competitor A with 35% share",
                "Growth calculated from 3-month trend"
            ],
            "alternative_classification": "question_mark",
            "alternative_reasoning": "If market share calculation is off by 20%"
        }
    ],
    "strategic_recommendations": {
        "stars": {
            "category": "star",
            "recommendations": [
                "Increase marketing budget by 30%",
                "Expand to 3 new locations"
            ],
            "consensus_level": "strong",
            "confidence": 0.85,
            "key_assumptions": ["Market growth continues", "Competition remains stable"],
            "alternative_views": ["CFO: Focus on margin over growth"],
            "risks": ["Market saturation", "Competitor response"]
        }
    },
    "market_positioning": {
        "overall_market_growth": 15.0,
        "competitive_intensity": "high",
        "market_maturity": "growth"
    },
    "confidence_by_category": {
        "stars": 0.85,
        "cash_cows": 0.90,
        "question_marks": 0.65,
        "dogs": 0.80
    },
    "data_quality_assessment": {
        "completeness": 0.85,
        "consistency": 0.90,
        "recency": 0.95,
        "sample_size_adequacy": 0.80,
        "overall_quality": 0.875,
        "missing_fields": ["competitor_data"],
        "data_gaps": ["Market size estimates"],
        "quality_issues": ["Some outliers in sales data"],
        "improvement_recommendations": [
            "Collect competitor pricing data",
            "Extend historical data to 12 months"
        ]
    },
    "overall_confidence": 0.80,
    "assumptions_made": [
        "Market growth is linear",
        "Competitor market shares are stable"
    ],
    "alternative_interpretations": [
        "If market is actually declining, Stars could be Question Marks"
    ],
    "limitations": [
        "Limited competitor data",
        "Short historical period (3 months)"
    ],
    "reasoning_chain": [
        "Step 1: Calculated market growth at 15% from 3-month trend",
        "Step 2: Identified market leader with 35% share",
        "Step 3: Classified products based on growth and relative share",
        "Step 4: Adjusted confidence based on data quality (0.875)",
        "Step 5: Synthesized recommendations from 3 expert perspectives"
    ]
}
```

---

## 🎓 Best Practices

### 1. Siempre Habilitar Multi-Perspective para Decisiones Críticas

```python
# ✅ Para decisiones estratégicas importantes
analysis = await agent.analyse_bcg_strategy(
    sales_data=data,
    enable_multi_perspective=True  # Reduce sesgo
)

# ⚠️ Para análisis rápidos, puede omitirse
quick_analysis = await agent.analyse_bcg_strategy(
    sales_data=data,
    enable_multi_perspective=False
)
```

### 2. Mostrar Razonamiento al Usuario

```python
# ✅ Transparencia genera confianza
analysis = await agent.analyse_bcg_strategy(
    sales_data=data,
    show_reasoning=True  # Usuario ve el proceso
)

# Mostrar en UI
for step in analysis.reasoning_chain:
    display_reasoning_step(step)
```

### 3. Verificar Calidad de Datos Primero

```python
# ✅ Evaluar calidad antes de confiar en resultados
quality = analysis.data_quality_assessment

if quality.overall_quality < 0.6:
    show_warning("Low data quality - results may be unreliable")
    show_recommendations(quality.improvement_recommendations)
```

### 4. Usar Audience-Targeted Summaries

```python
# ✅ Adaptar comunicación al público
if user.role == "owner":
    summary = await agent.generate_executive_summary(
        analysis, audience="restaurant_owner"
    )
elif user.role == "investor":
    summary = await agent.generate_executive_summary(
        analysis, audience="investor"
    )
```

### 5. Mostrar Confidence Scores

```python
# ✅ Ser honesto sobre incertidumbre
for category, confidence in analysis.confidence_by_category.items():
    if confidence < 0.7:
        show_warning(f"{category}: Low confidence ({confidence})")
```

---

## 🔥 Ventajas Competitivas

### vs Agentes Tradicionales

| Feature | Nosotros | Tradicional |
|---------|----------|-------------|
| **Razonamiento Visible** | ✅ Paso a paso | ❌ Caja negra |
| **Multi-Perspective** | ✅ 3 expertos | ❌ 1 perspectiva |
| **Uncertainty Quantification** | ✅ Confidence scores | ❌ No cuantifica |
| **Data Quality Awareness** | ✅ Evalúa antes | ❌ Asume buena calidad |
| **Audience Targeting** | ✅ 4 perfiles | ❌ Genérico |
| **Alternative Views** | ✅ Siempre muestra | ❌ No considera |
| **Assumptions Explicit** | ✅ Lista completa | ❌ Ocultas |

---

## 📝 Integración con Workflow

### En AnalysisOrchestrator

```python
from app.services.gemini.advanced_reasoning import AdvancedReasoningAgent

class AnalysisOrchestrator:
    def __init__(self):
        self.reasoning = AdvancedReasoningAgent()
    
    async def run_bcg_analysis(self, sales_data, menu_data):
        # Usar advanced reasoning para análisis estratégico
        analysis = await self.reasoning.analyse_bcg_strategy(
            sales_data=sales_data,
            menu_data=menu_data,
            enable_multi_perspective=True,
            show_reasoning=True
        )
        
        # Generar resumen para el usuario
        summary = await self.reasoning.generate_executive_summary(
            full_analysis=analysis.model_dump(),
            audience="restaurant_owner"
        )
        
        return {
            "analysis": analysis,
            "summary": summary,
            "confidence": analysis.overall_confidence,
            "data_quality": analysis.data_quality_assessment.overall_quality
        }
```

---

## 🚀 Casos de Uso Avanzados

### Caso 1: Análisis con Datos Incompletos

```python
# Datos con gaps
incomplete_data = [...]  # Faltan algunos campos

# El agente detecta y reporta problemas
analysis = await agent.analyse_bcg_strategy(
    sales_data=incomplete_data,
    menu_data=menu_data
)

# Verificar calidad
if analysis.data_quality_assessment.completeness < 0.7:
    print("⚠️ Data incomplete:")
    for field in analysis.data_quality_assessment.missing_fields:
        print(f"  Missing: {field}")
    
    # Mostrar recomendaciones
    print("\n💡 To improve analysis:")
    for rec in analysis.data_quality_assessment.improvement_recommendations:
        print(f"  - {rec}")
```

### Caso 2: Decisión con Alto Desacuerdo

```python
# Análisis con perspectivas divergentes
analysis = await agent.analyse_bcg_strategy(
    sales_data=data,
    enable_multi_perspective=True
)

# Identificar áreas de desacuerdo
for category, rec in analysis.strategic_recommendations.items():
    if rec.consensus_level in ["weak", "split"]:
        print(f"⚠️ {category}: Low consensus")
        print(f"  Main recommendation: {rec.recommendations[0]}")
        print(f"  Alternative views:")
        for alt in rec.alternative_views:
            print(f"    - {alt}")
        
        # Sugerir más investigación
        print("  💡 Recommendation: Gather more data before deciding")
```

### Caso 3: Comunicación Multi-Stakeholder

```python
# Generar múltiples versiones del mismo análisis
analysis = await agent.analyse_bcg_strategy(sales_data, menu_data)

# Para cada stakeholder
stakeholders = ["restaurant_owner", "investor", "operations_manager"]

summaries = {}
for stakeholder in stakeholders:
    summaries[stakeholder] = await agent.generate_executive_summary(
        full_analysis=analysis.model_dump(),
        audience=stakeholder,
        max_words=300
    )

# Enviar versión apropiada a cada uno
send_to_owner(summaries["restaurant_owner"])
send_to_investor(summaries["investor"])
send_to_ops(summaries["operations_manager"])
```

---

## 🎯 Métricas de Éxito

### Transparencia

```python
# Medir transparencia del razonamiento
transparency_score = len(analysis.reasoning_chain) / 5  # Esperamos ~5 pasos
print(f"Transparency: {transparency_score:.2f}")
```

### Consensus

```python
# Medir nivel de consenso
consensus_scores = {
    "unanimous": 1.0,
    "strong": 0.8,
    "moderate": 0.6,
    "weak": 0.4,
    "split": 0.2
}

avg_consensus = sum(
    consensus_scores[rec.consensus_level]
    for rec in analysis.strategic_recommendations.values()
) / len(analysis.strategic_recommendations)

print(f"Average consensus: {avg_consensus:.2f}")
```

---

**Última actualización:** 2026-02-03  
**Versión:** 1.0.0  
**Autor:** MenuPilot Team
