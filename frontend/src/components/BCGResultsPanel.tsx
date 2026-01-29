'use client'

import {
    BarChart3,
    ChevronDown,
    ChevronRight,
    Dog,
    DollarSign,
    HelpCircle,
    Milk,
    Percent,
    Star,
    Target
} from 'lucide-react'
import { useState } from 'react'
import {
    CartesianGrid,
    Cell,
    Label,
    ReferenceLine,
    ResponsiveContainer,
    Scatter,
    ScatterChart,
    Tooltip,
    XAxis,
    YAxis
} from 'recharts'

interface BCGClassification {
  name: string
  bcg_class: string
  bcg_label: string
  market_share: number
  growth_rate: number
  price?: number
  cost?: number
  gross_profit_per_unit?: number
  total_gross_profit?: number
  margin?: number
  overall_score: number
  strategy?: any
  priority?: string
}

interface BCGResultsPanelProps {
  data: {
    classifications: BCGClassification[]
    summary: {
      counts: Record<string, number>
      portfolio_health_score: number
    }
    ai_insights?: any
  }
}

const BCG_CONFIG = {
  star: { 
    icon: Star, 
    color: '#f59e0b', 
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200',
    label: 'Stars ⭐',
    description: 'Alto crecimiento, alta participación. INVERTIR.'
  },
  cash_cow: { 
    icon: Milk, 
    color: '#10b981', 
    bgColor: 'bg-emerald-50',
    borderColor: 'border-emerald-200',
    label: 'Cash Cows 🐄',
    description: 'Bajo crecimiento, alta participación. ORDEÑAR.'
  },
  question_mark: { 
    icon: HelpCircle, 
    color: '#6366f1', 
    bgColor: 'bg-indigo-50',
    borderColor: 'border-indigo-200',
    label: 'Question Marks ❓',
  },
  dog: { 
    icon: Dog, 
    color: '#ef4444', 
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    label: 'Dogs ',
    description: 'Bajo crecimiento, baja participaci\u00F3n. REVISAR.'
  }
}

export default function BCGResultsPanel({ data }: BCGResultsPanelProps) {
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({
    star: true,
    cash_cow: false,
    question_mark: false,
    dog: false
  })

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => ({ ...prev, [category]: !prev[category] }))
  }

  // Normalize data from backend (handles both legacy BCG and new Menu Engineering formats)
  const rawItems = data.items || data.classifications || []
  
  const normalizedItems = rawItems.map((item: any) => {
    // Map Menu Engineering categories to BCG equivalents for UI compatibility
    let category = (item.category || item.bcg_class || '').toLowerCase()
    if (category === 'plowhorse') category = 'cash_cow'
    if (category === 'puzzle') category = 'question_mark'
    
    // Map metrics for chart (X=Popularity, Y=CM)
    // If it's new format (Menu Engineering), use popularity_pct and cm_unitario
    // If it's legacy format, use market_share and growth_rate
    const x = item.popularity_pct !== undefined ? item.popularity_pct : (item.market_share || 0) * 100
    const y = item.cm_unitario !== undefined ? item.cm_unitario : (item.growth_rate || 0) * 100
    
    return {
      ...item,
      name: item.name,
      bcg_class: category,
      bcg_label: item.category_label || item.bcg_label || category,
      x,
      y,
      // Ensure metrics exist for display
      price: item.price || 0,
      margin: item.margin_pct ? item.margin_pct / 100 : item.margin || 0,
      growth_rate: item.growth_rate || 0,
      market_share: item.market_share || 0,
      overall_score: item.overall_score || 0,
      strategy: item.strategy
    }
  })

  // Group items by normalized category
  const groupedItems = normalizedItems.reduce((acc: any, item: any) => {
    const category = item.bcg_class
    if (!acc[category]) acc[category] = []
    acc[category].push(item)
    return acc
  }, {} as Record<string, any[]>)

  // Calculate summary counts if not present
  const counts = data.summary?.counts || {
    star: groupedItems['star']?.length || 0,
    cash_cow: groupedItems['cash_cow']?.length || 0,
    question_mark: groupedItems['question_mark']?.length || 0,
    dog: groupedItems['dog']?.length || 0
  }

  // Calculate health score if not present (simple weighted average of good categories)
  const calculateHealthScore = () => {
    if (data.summary?.portfolio_health_score !== undefined) return data.summary.portfolio_health_score
    
    const total = normalizedItems.length
    if (total === 0) return 0
    
    const stars = groupedItems['star']?.length || 0
    const cows = groupedItems['cash_cow']?.length || 0
    const puzzles = groupedItems['question_mark']?.length || 0
    
    // Stars & Cows are good (1.0), Puzzles okay (0.5), Dogs bad (0)
    return ((stars + cows) * 1.0 + puzzles * 0.5) / total
  }

  const healthScore = calculateHealthScore()

  // Calculate averages for reference lines
  const avgX = normalizedItems.reduce((sum: number, i: any) => sum + i.x, 0) / (normalizedItems.length || 1)
  const avgY = normalizedItems.reduce((sum: number, i: any) => sum + i.y, 0) / (normalizedItems.length || 1)

  // Get top item from each category
  const getTopItem = (category: string) => {
    const items = groupedItems[category] || []
    // Sort by contribution/score
    return items.sort((a: any, b: any) => (b.total_contribution || b.overall_score) - (a.total_contribution || a.overall_score))[0]
  }

  return (
    <div className="space-y-6">
      {/* Top 4 Category Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {(['star', 'cash_cow', 'question_mark', 'dog'] as const).map(category => {
          const config = BCG_CONFIG[category]
          const Icon = config.icon
          const count = counts[category] || 0
          const topItem = getTopItem(category)
          
          return (
            <div 
              key={category} 
              className={`${config.bgColor} ${config.borderColor} border rounded-xl p-4 cursor-pointer hover:shadow-md transition-all`}
              onClick={() => toggleCategory(category)}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Icon className="h-5 w-5" style={{ color: config.color }} />
                  <span className="font-semibold text-gray-900">{count}</span>
                </div>
                <span className="text-xs text-gray-500">{config.label.split(' ')[0]}</span>
              </div>
              <p className="text-xs text-gray-600 mb-2">{config.description}</p>
              {topItem && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs text-gray-500">Top:</p>
                  <p className="text-sm font-medium text-gray-800 truncate">{topItem.name}</p>
                  {topItem.margin && (
                    <p className="text-xs text-gray-500">
                      Margen: {(topItem.margin * 100).toFixed(0)}%
                    </p>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* BCG Matrix Chart */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary-500" />
          Matriz de Ingeniería de Menú (Popularidad vs Rentabilidad)
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart margin={{ top: 20, right: 40, bottom: 40, left: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              type="number" 
              dataKey="x" 
              name="Popularidad" 
              unit="%" 
              domain={[0, 'auto']}
              tick={{ fontSize: 12 }}
            >
              <Label value="Popularidad (% Mix)" offset={-10} position="insideBottom" style={{ fontSize: 12 }} />
            </XAxis>
            <YAxis 
              type="number" 
              dataKey="y" 
              name="Rentabilidad" 
              unit="$"
              tick={{ fontSize: 12 }}
            >
              <Label value="Margen de Contribución ($)" angle={-90} position="insideLeft" style={{ fontSize: 12 }} />
            </YAxis>
            <ReferenceLine x={avgX} stroke="#9ca3af" strokeDasharray="5 5" label="Avg Pop" />
            <ReferenceLine y={avgY} stroke="#9ca3af" strokeDasharray="5 5" label="Avg CM" />
            <Tooltip
              content={({ payload }) => {
                if (!payload || !payload[0]) return null
                const item = payload[0].payload
                return (
                  <div className="bg-white p-3 rounded-lg shadow-lg border text-sm">
                    <p className="font-semibold text-gray-900">{item.name}</p>
                    <p className="text-gray-600">{BCG_CONFIG[item.bcg_class as keyof typeof BCG_CONFIG]?.label || item.bcg_class}</p>
                    <div className="mt-2 space-y-1 text-xs">
                      <p>Popularidad: {item.x.toFixed(1)}%</p>
                      <p>Margen Contrib.: ${item.y.toFixed(2)}</p>
                      {item.margin && <p>Margen %: {(item.margin * 100).toFixed(0)}%</p>}
                      {item.price && <p>Precio: ${item.price.toFixed(2)}</p>}
                    </div>
                  </div>
                )
              }}
            />
            <Scatter data={normalizedItems} name="Productos">
              {normalizedItems.map((entry: any, idx: number) => (
                <Cell 
                  key={idx} 
                  fill={BCG_CONFIG[entry.bcg_class as keyof typeof BCG_CONFIG]?.color || '#666'} 
                />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
        
        {/* Legend */}
        <div className="flex justify-center gap-6 mt-4 flex-wrap">
          {Object.entries(BCG_CONFIG).map(([key, config]) => (
            <div key={key} className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: config.color }} />
              <span className="text-xs text-gray-600">{config.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Collapsible Product Lists by Category */}
      <div className="space-y-3">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <Target className="h-5 w-5 text-primary-500" />
          Productos por Categoría
        </h3>
        
        {(['star', 'cash_cow', 'question_mark', 'dog'] as const).map(category => {
          const config = BCG_CONFIG[category]
          const Icon = config.icon
          const items = groupedItems[category] || []
          const isExpanded = expandedCategories[category]
          
          if (items.length === 0) return null
          
          return (
            <div 
              key={category} 
              className={`${config.bgColor} ${config.borderColor} border rounded-xl overflow-hidden`}
            >
              {/* Header */}
              <button
                onClick={() => toggleCategory(category)}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-white/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Icon className="h-5 w-5" style={{ color: config.color }} />
                  <span className="font-semibold text-gray-900">{config.label}</span>
                  <span className="text-sm text-gray-500">({items.length} productos)</span>
                </div>
                {isExpanded ? (
                  <ChevronDown className="h-5 w-5 text-gray-400" />
                ) : (
                  <ChevronRight className="h-5 w-5 text-gray-400" />
                )}
              </button>
              
              {/* Expanded Content */}
              {isExpanded && (
                <div className="px-4 pb-4 space-y-2">
                  {items.sort((a: any, b: any) => (b.total_contribution || 0) - (a.total_contribution || 0)).map((item: any, idx: number) => (
                    <div 
                      key={idx} 
                      className="bg-white rounded-lg p-3 flex items-center justify-between"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-gray-900">{item.name}</span>
                          {item.priority === 'high' && (
                            <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                              Prioridad Alta
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                          {item.price && (
                            <span className="flex items-center gap-1">
                              <DollarSign className="h-3 w-3" />
                              ${item.price.toFixed(2)}
                            </span>
                          )}
                          {item.margin && (
                            <span className="flex items-center gap-1">
                              <Percent className="h-3 w-3" />
                              {(item.margin * 100).toFixed(0)}% margen
                            </span>
                          )}
                          {item.total_contribution !== undefined && (
                            <span className="flex items-center gap-1 text-primary-600">
                              <DollarSign className="h-3 w-3" />
                              ${item.total_contribution.toFixed(0)} Contrib. Total
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold" style={{ color: config.color }}>
                          {item.x.toFixed(1)}%
                        </div>
                        <div className="text-xs text-gray-400">Popularidad</div>
                      </div>
                    </div>
                  ))}
                  
                  {/* Strategy Summary */}
                  {items[0]?.strategy && (
                    <div className="mt-3 p-3 bg-white/70 rounded-lg border border-gray-100">
                      <p className="text-sm font-medium text-gray-700 mb-1">
                        Estrategia Recomendada:
                      </p>
                      <p className="text-sm text-gray-600">
                        {typeof items[0].strategy === 'object' 
                          ? items[0].strategy.summary || items[0].strategy.action 
                          : items[0].strategy}
                      </p>
                      {items[0].strategy.recommendations && (
                        <ul className="mt-2 list-disc list-inside text-xs text-gray-600">
                          {items[0].strategy.recommendations.slice(0, 3).map((rec: string, i: number) => (
                            <li key={i}>{rec}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Portfolio Health Score */}
      <div className="bg-gradient-to-r from-primary-50 to-indigo-50 rounded-xl p-4 border border-primary-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-900">Salud del Portafolio</h3>
            <p className="text-sm text-gray-600 mt-1">
              Score basado en balance de categorías
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-primary-600">
              {(healthScore * 100).toFixed(0)}%
            </div>
            <div className="text-sm text-gray-500">
              {healthScore >= 0.7 ? 'Saludable' : 
               healthScore >= 0.5 ? 'Moderado' : 'Necesita atención'}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
