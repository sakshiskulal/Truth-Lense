import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'
import { Activity, TrendingUp, AlertTriangle } from 'lucide-react'

const TrustScoreChart = ({ analysis }) => {
  // Pie chart data for analysis breakdown
  const pieData = [
    { 
      name: 'AI Detection', 
      value: analysis.ai_analysis?.score * 100 || 0, 
      color: '#3b82f6',
      details: analysis.ai_analysis?.model || 'Lightweight CV'
    },
    { 
      name: 'Azure Analysis', 
      value: analysis.azure_checked ? (analysis.azure_analysis?.score * 100 || 0) : 0, 
      color: '#10b981',
      details: analysis.azure_checked ? 'Available' : 'Not Available'
    },
    { 
      name: 'News Verification', 
      value: analysis.news_checked ? (analysis.news_analysis?.found ? 100 : 0) : 0, 
      color: '#f59e0b',
      details: analysis.news_checked ? `${analysis.news_analysis?.article_count || 0} articles` : 'Not Available'
    }
  ]

  // Bar chart data for technical features
  const featureData = analysis.features ? [
    {
      name: 'Edge Density',
      value: (analysis.features.edge_density || 0) * 100,
      threshold: 8,
      color: (analysis.features.edge_density || 0) * 100 < 8 ? '#ef4444' : '#10b981'
    },
    {
      name: 'Texture Variance',
      value: Math.min((analysis.features.texture_variance || 0) / 10, 100),
      threshold: 20,
      color: (analysis.features.texture_variance || 0) < 200 ? '#ef4444' : '#10b981'
    },
    {
      name: 'Suspicious Score',
      value: (analysis.features.suspicious_score || 0) * 100,
      threshold: 50,
      color: (analysis.features.suspicious_score || 0) * 100 > 50 ? '#ef4444' : '#10b981'
    }
  ] : []

  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    if (percent < 0.05) return null
    const RADIAN = Math.PI / 180
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize={12}
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    )
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border">
          <p className="font-medium text-gray-900">{data.name}</p>
          <p className="text-sm text-gray-600">Score: {payload[0].value.toFixed(1)}%</p>
          <p className="text-xs text-gray-500">{data.details}</p>
        </div>
      )
    }
    return null
  }

  const FeatureTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border">
          <p className="font-medium text-gray-900">{data.name}</p>
          <p className="text-sm text-gray-600">Value: {payload[0].value.toFixed(1)}%</p>
          <p className="text-xs text-gray-500">
            Threshold: {data.threshold}% 
            {payload[0].value > data.threshold ? ' (Above threshold)' : ' (Below threshold)'}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-6">
      {/* Analysis Breakdown Chart */}
      {/* <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
          <Activity className="w-5 h-5" />
          <span>Analysis Breakdown</span>
        </h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderCustomizedLabel}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
        
        {/* Summary stats */}
        {/* <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
          {pieData.map((item, index) => (
            <div key={index} className="text-center">
              <div className="flex items-center justify-center space-x-2 mb-1">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: item.color }}
                ></div>
                <span className="text-xs font-medium text-gray-700">{item.name}</span>
              </div>
              <p className="text-lg font-bold text-gray-900">{item.value.toFixed(0)}%</p>
              <p className="text-xs text-gray-500">{item.details}</p>
            </div>
          ))}
        </div>
      </div> */}

      {/* Technical Features Chart */}
      {featureData.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <TrendingUp className="w-5 h-5" />
            <span>Technical Analysis</span>
          </h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featureData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  tick={{ fontSize: 12 }}
                  interval={0}
                  angle={-45}
                  textAnchor="end"
                  height={60}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip content={<FeatureTooltip />} />
                <Bar dataKey="value" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <AlertTriangle className="w-4 h-4 text-yellow-500" />
              <span className="text-sm font-medium text-gray-700">Feature Analysis</span>
            </div>
            <p className="text-xs text-gray-600">
              Technical features extracted from the content. Values below certain thresholds may indicate potential manipulation.
            </p>
          </div>
        </div>
      )}

      {/* Analysis Summary */}
      {analysis.anomalies && analysis.anomalies.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Summary</h3>
          <div className="grid grid-cols-1 gap-3">
            <div className="flex items-center space-x-3 p-3 bg-red-50 rounded-lg border border-red-200">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              <div>
                <p className="text-sm font-medium text-red-900">
                  {analysis.anomalies.length} anomal{analysis.anomalies.length === 1 ? 'y' : 'ies'} detected
                </p>
                <p className="text-xs text-red-700">
                  {analysis.anomalies.filter(a => a.severity === 'high').length} high severity, {' '}
                  {analysis.anomalies.filter(a => a.severity === 'medium').length} medium severity
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TrustScoreChart