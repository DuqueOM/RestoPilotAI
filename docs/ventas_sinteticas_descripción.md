# 📊 ANÁLISIS ESTADÍSTICO DETALLADO - DICIEMBRE 2025
## Bar-Restaurante Margarita

---

## 🎯 **RESUMEN EJECUTIVO**

**Período analizado:** 01-12-2025 a 31-12-2025 (31 días)
**Datos filtrados:** 354 transacciones | 2,421 productos individuales

### Métricas Clave del Mes

| Métrica | Valor | Comparación |
|---------|-------|-------------|
| **Total Vendido** | $179,223,374 COP | 11.13% del año 2025 |
| **Ticket Promedio** | $506,281 COP | +2.86% vs promedio anual |
| **Transacciones** | 354 | 10.82% del año |
| **Trans/Día** | 11.4 | - |
| **Margen Bruto** | 56.20% | Consistente con anual |

**⭐ Diciembre es el mes de MAYOR VENTA del año** debido a la estacionalidad festiva (+35% vs meses normales)

---

**Columnas (29)**

### Identificación y Tiempo (10 columnas):

id_transaccion - ID único (TRX0000001 - TRX0009844)
date - Fecha formato DD-MM-YY
hora - Hora formato HH:MM
timestamp - Fecha y hora completa
dia_semana - Lunes, Martes, etc. (validado)
mes - 1-12
año - 2023, 2024, 2025
es_festivo - TRUE/FALSE (días festivos colombianos)
es_fin_semana - TRUE/FALSE (Vie/Sáb/Dom)
periodo_dia - Tarde/Noche/Late Night

### Operacionales (6 columnas):

mesa - Número 1-30
tipo_mesa - Barra/Salón
num_personas - 1-8 personas
mesero - Mesero_01 a Mesero_08
metodo_pago - Efectivo, Tarjeta Débito/Crédito, Transferencia, Mixto
duracion_minutos - 45-120 minutos

### Producto Individual (5 columnas):

item_name - Nombre del producto (ej: "Margarita", "Corona")
categoria - Categoría (ej: "Coctelería", "Cerveza")
units_sold- Unidades de ESTE producto vendidas en el mismo tiket (1-7)
price - Precio unitario con inflación
cost - Costo unitario con inflación

### Totales del Ticket (8 columnas):

productos por tiket- Total items en el ticket completo
productos_en_tiket - Total productos (igual a units_sold)
subtotal_tiket - Suma de precios sin propina
propina_en_tiket - Propina (8-15% del subtotal)
tiket_total - Total con propina incluida
margen_bruto_tiket - Margen bruto (subtotal - costos)
margen_porcentaje_tiket - Margen como porcentaje
ticket_promedio_persona - Total / num_personas

---

## 💰 **1. MÉTRICAS FINANCIERAS GLOBALES**

### Ventas Totales
| Período | Monto |
|---------|-------|
| **Mes completo** | $179,223,374 COP |
| **Promedio diario** | $5,781,399 COP |
| **Promedio semanal** | $40,456,744 COP |

### Distribución de Tickets

| Estadístico | Valor |
|-------------|-------|
| **Promedio** | $506,281 COP |
| **Mediana** | $418,286 COP |
| **Mínimo** | $9,263 COP |
| **Máximo** | $3,440,087 COP |
| **Desviación Estándar** | $428,017 COP |

**Interpretación:** El ticket mediano ($418K) es menor que el promedio ($506K), indicando que hay algunos tickets muy altos que elevan el promedio (grupos grandes o botellas premium).

### Transacciones y Productos

| Métrica | Valor |
|---------|-------|
| **Transacciones totales** | 354 |
| **Productos vendidos** | 2,551 unidades |
| **Productos/transacción** | 6.84 (promedio) |
| **Rango productos/ticket** | 1 - 25 productos |

---

## 📅 **2. DISTRIBUCIÓN TEMPORAL**

### Por Día de la Semana

| Día | Transacciones | % Total | Ventas | % Ventas | Ticket Prom |
|-----|---------------|---------|--------|----------|-------------|
| **Sábado** | 85 | 24.0% | $46,933,072 | **26.19%** | $552,154 |
| **Viernes** | 74 | 20.9% | $42,944,296 | **23.96%** | $580,328 |
| **Jueves** | 48 | 13.6% | $21,991,856 | 12.27% | $458,164 |
| **Miércoles** | 45 | 12.7% | $20,354,541 | 11.36% | $452,323 |
| **Martes** | 36 | 10.2% | $18,649,279 | 10.41% | $518,036 |
| **Domingo** | 35 | 9.9% | $13,857,944 | 7.73% | $395,941 |
| **Lunes** | 31 | 8.8% | $14,492,386 | 8.09% | $467,496 |

**🔥 Fin de semana (Vie-Sáb-Dom):** 50.1% de las ventas del mes

**Insights:**
- Sábados y viernes concentran el **50% de las ventas**
- Viernes tiene el ticket promedio más alto ($580K)
- Domingos tienen el ticket más bajo (post-fiesta)

### Por Período del Día

| Período | Horario | Trans. | % Trans | Ventas | % Ventas | Ticket Prom |
|---------|---------|--------|---------|--------|----------|-------------|
| **Noche** | 21:00-23:00 | 249 | 70.3% | $139,172,062 | **77.65%** | $558,924 |
| **Tarde** | 16:00-19:00 | 79 | 22.3% | $22,798,985 | 12.72% | $288,595 |
| **Late Night** | 23:00-02:00 | 26 | 7.3% | $17,252,327 | 9.63% | $663,551 |

**📈 Insight clave:** El período de noche genera casi el **80% de las ventas** con tickets 2x más altos que la tarde.

### Top 10 Horas con Mayores Ventas

| Hora | Trans. | Ventas | % Total |
|------|--------|--------|---------|
| 23:16 | 1 | $3,440,087 | 1.92% |
| 20:47 | 3 | $3,327,325 | 1.86% |
| 19:55 | 4 | $3,100,071 | 1.73% |
| 19:46 | 4 | $2,872,001 | 1.60% |
| 20:58 | 3 | $2,865,042 | 1.60% |
| 20:49 | 5 | $2,785,885 | 1.55% |
| 20:53 | 3 | $2,601,964 | 1.45% |
| 22:06 | 1 | $2,515,538 | 1.40% |
| 19:43 | 3 | $2,496,416 | 1.39% |
| 19:07 | 5 | $2,379,373 | 1.33% |

**Pico de ventas:** 19:00 - 21:00 (hora de cena)

---

## 🏆 **3. PRODUCTOS Y CATEGORÍAS**

### Top 20 Productos Más Vendidos

| Pos. | Producto | Unidades | Precio Prom | Categoría |
|------|----------|----------|-------------|-----------|
| 1 | **Chivas 12** | 129 | $50,179 | Whisky |
| 2 | **Heineken** | 97 | $16,229 | Cerveza |
| 3 | **Nachos** | 91 | $32,459 | Snacks |
| 4 | **Corona** | 91 | $16,229 | Cerveza |
| 5 | **Club Colombia** | 89 | $11,592 | Cerveza |
| 6 | **Stella Artois** | 89 | $16,229 | Cerveza |
| 7 | **Olmeca Altos** | 70 | $50,473 | Tequila |
| 8 | **José Cuervo** | 68 | $48,882 | Tequila |
| 9 | **Gato Negro** | 51 | $115,927 | Vino |
| 10 | **Casillero del Diablo** | 50 | $115,927 | Vino |
| 11 | Ron Viejo de Caldas | 44 | $150,705 | Ron |
| 12 | Bacardí Limón | 43 | $185,483 | Ron |
| 13 | Hervido con Ron | 40 | $23,185 | Coctelería |
| 14 | Absolut Mandrin | 35 | $220,262 | Vodka |
| 15 | Tom Collins | 35 | $39,415 | Coctelería |
| 16 | Chorizo Santarrosano | 35 | $20,866 | Entradas |
| 17 | Brownie con Helado | 33 | $13,911 | Postres |
| 18 | Gin Tonic | 31 | $39,415 | Coctelería |
| 19 | Hervido con Brandy | 31 | $23,185 | Coctelería |
| 20 | Beefeater | 30 | $301,411 | Ginebra |

**🥃 Producto estrella:** Chivas 12 (129 unidades - más del doble que otros whiskies)
**🍺 Cervezas dominan:** 4 de las 6 posiciones más vendidas

### Top 15 Categorías por Ingresos

| Categoría | Unidades | Ingresos | % Total |
|-----------|----------|----------|---------|
| **Ginebra** | 78 | $28,135,548 | 17.47% |
| **Coctelería** | 677 | $25,027,309 | 15.54% |
| **Whisky** | 162 | $19,180,100 | 11.91% |
| **Vodka** | 94 | $17,760,045 | 11.03% |
| **Ron** | 87 | $14,606,789 | 9.07% |
| **Vino** | 101 | $11,708,627 | 7.27% |
| **Tequila** | 149 | $9,900,139 | 6.15% |
| **Cerveza** | 366 | $5,527,121 | 3.43% |
| Mariscos | 46 | $3,070,888 | 1.91% |
| Snacks | 91 | $2,953,769 | 1.83% |
| Salmón | 39 | $2,743,968 | 1.70% |
| Carnes | 48 | $2,682,546 | 1.67% |
| Entradas | 87 | $2,041,428 | 1.27% |
| Costillas | 38 | $1,982,346 | 1.23% |
| Pastas | 44 | $1,581,228 | 0.98% |

**Mix Bebidas vs Comida:**
- **Bebidas:** ~82% de los ingresos
- **Comida:** ~18% de los ingresos

**💡 Insight:** En diciembre (mes festivo) las bebidas premium dominan aún más que en meses normales.

---

## 👥 **4. COMPORTAMIENTO DE CLIENTES**

### Distribución por Tamaño de Grupo

| Personas | Trans. | % | Ticket Total | Ticket Per Cápita |
|----------|--------|---|--------------|-------------------|
| **1** | 68 | 19.2% | $148,339 | $148,339 |
| **2** | 98 | 27.7% | $385,554 | $192,777 |
| **3** | 90 | 25.4% | $495,491 | $165,164 |
| **4** | 48 | 13.6% | $731,957 | $182,989 |
| **5** | 37 | 10.5% | $909,998 | $182,000 |
| **6** | 4 | 1.1% | $2,014,534 | $335,756 |
| **7** | 7 | 2.0% | $680,855 | $97,265 |
| **8** | 2 | 0.6% | $2,564,890 | $320,612 |

**Insights:**
- **53% de transacciones** son de 1-2 personas
- Grupos grandes (5+) representan solo el **14%** pero con tickets muy altos
- El gasto per cápita es mayor en grupos de 2 personas ($192K) que en grupos grandes

### Por Tipo de Mesa

| Tipo | Trans. | % | Ticket Prom | Total Vendido |
|------|--------|---|-------------|---------------|
| **Salón** | 308 | 87.0% | $536,626 | $165,280,654 |
| **Barra** | 46 | 13.0% | $303,103 | $13,942,720 |

**📊 El salón genera el 92% de las ventas** con tickets 77% más altos que la barra.

---

## 💳 **5. MÉTODOS DE PAGO**

| Método | Transacciones | % Trans | Monto | % Monto |
|--------|---------------|---------|-------|---------|
| **Tarjeta Crédito** | 149 | 42.1% | $74,347,017 | 41.5% |
| **Efectivo** | 86 | 24.3% | $41,883,202 | 23.4% |
| **Tarjeta Débito** | 65 | 18.4% | $38,155,354 | 21.3% |
| **Transferencia** | 30 | 8.5% | $14,065,623 | 7.9% |
| **Mixto** | 24 | 6.8% | $10,772,178 | 6.0% |

**💳 Tarjeta de crédito domina** en diciembre (mes de compras navideñas)

---

## 📆 **6. ANÁLISIS POR DÍAS ESPECÍFICOS**

### Top 10 Días con Mayores Ventas

| Fecha | Día Semana | Trans. | Ventas | Ticket Prom |
|-------|------------|--------|--------|-------------|
| **13-12** | Sábado | 22 | $13,887,219 | $631,237 |
| **27-12** | Sábado | 18 | $13,382,932 | $743,496 |
| **20-12** | Sábado | 24 | $12,682,114 | $528,421 |
| **19-12** | Viernes | 19 | $12,491,622 | $657,454 |
| **05-12** | Viernes | 19 | $12,086,203 | $636,116 |
| **26-12** | Viernes | 20 | $10,926,380 | $546,319 |
| **04-12** | Jueves | 11 | $7,540,003 | $685,455 |
| **12-12** | Viernes | 16 | $7,440,091 | $465,006 |
| **06-12** | Sábado | 21 | $6,980,807 | $332,419 |
| **25-12** | Jueves | 15 | $5,958,705 | $397,247 |

**🎄 Patrones navideños:**
- **27 de diciembre** (post-navidad) tiene el ticket promedio MÁS ALTO ($743K)
- **25 de diciembre** (Navidad) tiene ventas moderadas
- Los sábados 13, 20 y 27 son los días estrella

---

## 🎉 **7. IMPACTO DE DÍAS FESTIVOS**

### Comparación Festivos vs Normales

| Tipo | Trans. | Total Vendido | Ticket Prom |
|------|--------|---------------|-------------|
| **Festivos** | 33 | $15,519,894 | $470,300 |
| **Normales** | 321 | $163,703,480 | $509,980 |

**Incremento en festivos:** -7.78%

**🤔 Sorpresa:** En diciembre, los días festivos tienen tickets MENORES que los días normales. Esto puede deberse a:
1. Gente celebra en casa en días como Navidad (25-12)
2. Los festivos son días entre semana con menos tráfico
3. Los fines de semana normales tienen más celebraciones

---

## 📦 **8. ESTADÍSTICAS DE PRODUCTOS POR TRANSACCIÓN**

| Métrica | Valor |
|---------|-------|
| **Promedio** | 6.84 productos |
| **Mediana** | 6 productos |
| **Mínimo** | 1 producto |
| **Máximo** | 25 productos |
| **Desv. Estándar** | 4.11 |

**📊 Distribución típica:** La mayoría de tickets tienen entre 3-10 productos.

---

## 📈 **9. COMPARACIÓN CON EL TOTAL ANUAL 2025**

| Métrica | Diciembre | Total 2025 | % del Año |
|---------|-----------|------------|-----------|
| **Transacciones** | 354 | 3,271 | 10.82% |
| **Ventas** | $179,223,374 | $1,609,957,804 | **11.13%** |
| **Ticket Promedio** | $506,281 | $492,191 | +2.86% |

**🎯 Conclusión:** Diciembre representa el **11.13% de las ventas anuales** con solo el 8.33% de los días del año (31/365).

**⭐ Factor de estacionalidad:** Diciembre tiene ventas **34% superiores** al promedio mensual.

---

## 💡 **INSIGHTS ESTRATÉGICOS**

### Fortalezas de Diciembre 2025

✅ **Ticket promedio alto** ($506K vs $492K anual)
✅ **Concentración en fin de semana** (50% de ventas)
✅ **Bebidas premium dominan** (82% de ingresos)
✅ **Margen saludable** (56.2%)
✅ **Peak de ventas nocturnas** (77% entre 21:00-23:00)

### Oportunidades de Mejora

🔶 **Domingos bajos** (solo 7.7% de ventas) - Posible promoción de brunch
🔶 **Barra subutilizada** (13% de transacciones) - Aumentar atractivo
🔶 **Comida representa solo 18%** - Oportunidad de upsell
🔶 **Días festivos con tickets bajos** - Revisar estrategia festivos

### Recomendaciones

1. **Maximizar fines de semana:** Staff completo vie-sáb
2. **Promociones de tarde:** Happy hour 17:00-19:00 para aumentar tráfico
3. **Combos comida+bebida:** Incrementar venta de alimentos
4. **Eventos especiales domingos:** Música en vivo o temáticas
5. **Menú de celebración:** Para grupos grandes (6+ personas)

---

## 📊 **RESUMEN FINAL**

**Diciembre 2025 fue un mes EXCELENTE:**
- ✅ $179.2M COP vendidos (11.13% del año)
- ✅ 354 transacciones (11.4/día)
- ✅ Ticket promedio $506K (+2.86% vs anual)
- ✅ Margen bruto 56.2%
- ✅ Estacionalidad positiva (+34% vs promedio)

**El mes demuestra el poder de la temporada festiva** y valida el modelo de negocio con fuerte énfasis en coctelería premium y bebidas destiladas.

---

**📧 Documento generado:** Enero 2025
**Fuente:** ventas_sinteticas_CORREGIDO.csv
**Período analizado:** Diciembre 2025 (31 días)
