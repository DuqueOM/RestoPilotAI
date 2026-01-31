'use client'

import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine, Label } from 'recharts'
import { Star, Milk, HelpCircle, Dog } from 'lucide-react'

interface BCGChartProps {
  data: {
    classifications: Array<{
      name: string
      bcg_class: string
      bcg_label: string
      market_share: number
      growth_rate: number
      overall_score: number
    }>
    summary: {
      counts: Record<string, number>
      portfolio_health_score: number
    }
  }
}

const BCG_COLORS = {
  star: '#f59e0b',
  cash_cow: '#10b981',
  question_mark: '#6366f1',
  dog: '#ef4444'
}

const BCG_ICONS = {
  star: Star,
  cash_cow: Milk,
  question_mark: HelpCircle,
  dog: Dog
}

export default function BCGChart({ data }: BCGChartProps) {
  const chartData = data.classifications.map(item => ({
    ...item,
    x: item.market_share * 100,
    y: item.growth_rate * 100
  }))

  const avgShare = chartData.reduce((sum, i) => sum + i.x, 0) / chartData.length || 50
  const avgGrowth = chartData.reduce((sum, i) => sum + i.y, 0) / chartData.length || 0

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(data.summary.counts).map(([key, count]) => {
          const Icon = BCG_ICONS[key as keyof typeof BCG_ICONS] || Star
          return (
            <div key={key} className="bg-gray-50 rounded-lg p-4 flex items-center gap-3">
              <div className="p-2 rounded-full" style={{ backgroundColor: `${BCG_COLORS[key as keyof typeof BCG_COLORS]}20` }}>
                <Icon className="h-5 w-5" style={{ color: BCG_COLORS[key as keyof typeof BCG_COLORS] }} />
              </div>
              <div>
                <p className="text-2xl font-bold">{count}</p>
                <p className="text-sm text-gray-500 capitalize">{key.replace('_', ' ')}s</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* BCG Matrix Chart */}
      <div className="bg-gray-50 rounded-lg p-4">
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 40, left: 40 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" dataKey="x" name="Market Share" unit="%" domain={[0, 'auto']}>
              <Label value="Market Share (%)" offset={-10} position="insideBottom" />
            </XAxis>
            <YAxis type="number" dataKey="y" name="Growth Rate" unit="%">
              <Label value="Growth Rate (%)" angle={-90} position="insideLeft" />
            </YAxis>
            <ReferenceLine x={avgShare} stroke="#666" strokeDasharray="5 5" />
            <ReferenceLine y={avgGrowth} stroke="#666" strokeDasharray="5 5" />
            <Tooltip
              content={({ payload }) => {
                if (!payload || !payload[0]) return null
                const item = payload[0].payload
                return (
                  <div className="bg-white p-3 rounded-lg shadow-lg border">
                    <p className="font-semibold">{item.name}</p>
                    <p className="text-sm text-gray-600">Class: {item.bcg_label}</p>
                    <p className="text-sm">Share: {item.x.toFixed(1)}%</p>
                    <p className="text-sm">Growth: {item.y.toFixed(1)}%</p>
                    <p className="text-sm">Score: {(item.overall_score * 100).toFixed(0)}</p>
                  </div>
                )
              }}
            />
            <Scatter data={chartData}>
              {chartData.map((entry, idx) => (
                <Cell key={idx} fill={BCG_COLORS[entry.bcg_class as keyof typeof BCG_COLORS] || '#666'} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Items List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data.classifications.map((item, idx) => (
          <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: BCG_COLORS[item.bcg_class as keyof typeof BCG_COLORS] }} />
            <div className="flex-1">
              <p className="font-medium">{item.name}</p>
              <p className="text-sm text-gray-500">{item.bcg_label} • Score: {(item.overall_score * 100).toFixed(0)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
