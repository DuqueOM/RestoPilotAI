'use client'

import { 
  BarChart3, 
  ChevronDown, 
  ChevronRight, 
  DollarSign,
  HelpCircle, 
  Milk, 
  Star, 
  Dog,
  TrendingUp,
  TrendingDown,
  Target,
  Percent
} from 'lucide-react'
import { useState } from 'react'
import { 
  ScatterChart, 
  Scatter, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Cell, 
  ReferenceLine, 
  Label,
  Legend
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
    description: 'Alto crecimiento, baja participación. ANALIZAR.'
  },
  dog: { 
    icon: Dog, 
    color: '#ef4444', 
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    label: 'Dogs 🐕',
    description: 'Bajo crecimiento, baja participación. REVISAR.'
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

  // Group items by BCG class
  const groupedItems = data.classifications.reduce((acc, item) => {
    const bcgClass = item.bcg_class
    if (!acc[bcgClass]) acc[bcgClass] = []
    acc[bcgClass].push(item)
    return acc
  }, {} as Record<string, BCGClassification[]>)

  // Prepare chart data
  const chartData = data.classifications.map(item => ({
    ...item,
    x: item.market_share * 100,
    y: item.growth_rate * 100
  }))

  const avgShare = chartData.reduce((sum, i) => sum + i.x, 0) / chartData.length || 50
  const avgGrowth = chartData.reduce((sum, i) => sum + i.y, 0) / chartData.length || 0

  // Get top item from each category
  const getTopItem = (category: string) => {
    const items = groupedItems[category] || []
    return items.sort((a, b) => b.overall_score - a.overall_score)[0]
  }

  return (
    <div className="space-y-6">
      {/* Top 4 Category Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {(['star', 'cash_cow', 'question_mark', 'dog'] as const).map(category => {
          const config = BCG_CONFIG[category]
          const Icon = config.icon
          const count = data.summary.counts[category] || 0
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
          Matriz BCG - Posicionamiento de Productos
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart margin={{ top: 20, right: 40, bottom: 40, left: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              type="number" 
              dataKey="x" 
              name="Participación en Profit" 
              unit="%" 
              domain={[0, 'auto']}
              tick={{ fontSize: 12 }}
            >
              <Label value="Participación en Gross Profit (%)" offset={-10} position="insideBottom" style={{ fontSize: 12 }} />
            </XAxis>
            <YAxis 
              type="number" 
              dataKey="y" 
              name="Crecimiento" 
              unit="%"
              tick={{ fontSize: 12 }}
            >
              <Label value="Tasa de Crecimiento (%)" angle={-90} position="insideLeft" style={{ fontSize: 12 }} />
            </YAxis>
            <ReferenceLine x={avgShare} stroke="#9ca3af" strokeDasharray="5 5" />
            <ReferenceLine y={avgGrowth} stroke="#9ca3af" strokeDasharray="5 5" />
            <Tooltip
              content={({ payload }) => {
                if (!payload || !payload[0]) return null
                const item = payload[0].payload as BCGClassification & { x: number; y: number }
                return (
                  <div className="bg-white p-3 rounded-lg shadow-lg border text-sm">
                    <p className="font-semibold text-gray-900">{item.name}</p>
                    <p className="text-gray-600">{item.bcg_label}</p>
                    <div className="mt-2 space-y-1 text-xs">
                      <p>Participación: {item.x.toFixed(1)}%</p>
                      <p>Crecimiento: {item.y.toFixed(1)}%</p>
                      {item.margin && <p>Margen: {(item.margin * 100).toFixed(0)}%</p>}
                      {item.price && <p>Precio: ${item.price.toFixed(2)}</p>}
                      <p>Score: {(item.overall_score * 100).toFixed(0)}</p>
                    </div>
                  </div>
                )
              }}
            />
            <Scatter data={chartData} name="Productos">
              {chartData.map((entry, idx) => (
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
          Productos por Categoría BCG
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
                  {items.sort((a, b) => b.overall_score - a.overall_score).map((item, idx) => (
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
                          {item.growth_rate !== undefined && (
                            <span className={`flex items-center gap-1 ${item.growth_rate > 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {item.growth_rate > 0 ? (
                                <TrendingUp className="h-3 w-3" />
                              ) : (
                                <TrendingDown className="h-3 w-3" />
                              )}
                              {(item.growth_rate * 100).toFixed(0)}% crecimiento
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold" style={{ color: config.color }}>
                          {(item.overall_score * 100).toFixed(0)}
                        </div>
                        <div className="text-xs text-gray-400">Score</div>
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
                          ? items[0].strategy.summary 
                          : items[0].strategy}
                      </p>
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
              Score basado en balance de categorías BCG
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-primary-600">
              {(data.summary.portfolio_health_score * 100).toFixed(0)}%
            </div>
            <div className="text-sm text-gray-500">
              {data.summary.portfolio_health_score >= 0.7 ? 'Saludable' : 
               data.summary.portfolio_health_score >= 0.5 ? 'Moderado' : 'Necesita atención'}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
