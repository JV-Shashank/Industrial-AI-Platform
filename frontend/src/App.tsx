
import {
  useCallback,
  useEffect,
  useState
} from 'react'
import './App.css'


import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'



type MachineReadings = {
  air_temperature: number
  process_temperature: number
  rotational_speed: number
  torque: number
  tool_wear: number
  product_type: 'L' | 'M' | 'H'
}

type Prediction = {
  id: number
  model_name: string
  failure_probability: number
  decision_threshold: number
  predicted_failure: number
  status: string
  risk_level: string
  created_at: string
}

const initialReadings: MachineReadings = {
  air_temperature: 300,
  process_temperature: 310,
  rotational_speed: 1500,
  torque: 40,
  tool_wear: 100,
  product_type: 'M',
}



type Analytics = {
  total_predictions: number
  predicted_failures: number
  predicted_normal: number
  average_failure_probability: number
  risk_distribution: {
    risk_level: string
    count: number
  }[]
  recent_predictions: {
    id: number
    created_at: string
    failure_probability: number
    predicted_failure: number
    risk_level: string
  }[]
}

const RISK_COLORS: Record<string, string> = {
  Low: '#50d5a5',
  Medium: '#f5c76b',
  High: '#ff8585',
}





function App() {
  const [readings, setReadings] =
    useState<MachineReadings>(initialReadings)

  const [result, setResult] = useState<Prediction | null>(null)
  const [history, setHistory] = useState<Prediction[]>([])
  const [loading, setLoading] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(true)
  const [error, setError] = useState('')
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [analyticsError, setAnalyticsError] = useState('')



  
const loadAnalytics = useCallback(async () => {
    try {
      const response = await fetch('/api/analytics/summary')

      if (!response.ok) {
        throw new Error('Could not load analytics.')
      }

      const data: Analytics = await response.json()
      setAnalytics(data)
      setAnalyticsError('')
    } catch (err) {
      setAnalyticsError(
        err instanceof Error ? err.message : 'Analytics unavailable.',
      )
    }
  }, [])


  const loadHistory = useCallback(async () => {
    setHistoryLoading(true)

    try {
      const response = await fetch('/api/predictions?limit=10')

      if (!response.ok) {
        throw new Error('Could not load prediction history.')
      }

      const data = await response.json()
      setHistory(data.predictions)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Unable to load history.',
      )
    } finally {
      setHistoryLoading(false)
    }
  }, [])

  useEffect(() => {
  void loadHistory()
  void loadAnalytics()
}, [loadHistory, loadAnalytics])

  function updateField(
    field: keyof MachineReadings,
    value: number | 'L' | 'M' | 'H',
  ) {
    setReadings((previous) => ({
      ...previous,
      [field]: value,
    }))
  }

  async function submitPrediction(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(readings),
      })

      if (!response.ok) {
        const body = await response.json()
        const detail = body.detail
        throw new Error(
          typeof detail === 'string'
            ? detail
            : 'The prediction request failed. Check the sensor values.',
        )
      }


      const prediction: Prediction = await response.json()
      setResult(prediction)

      await loadHistory()
      await loadAnalytics()

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Could not connect to the prediction service.',
      )
    } finally {
      setLoading(false)
    }
  }

  const fields: {
    key: keyof Omit<MachineReadings, 'product_type'>
    label: string
    unit: string
    min: number
    max: number
    step: number
  }[] = [
    {
      key: 'air_temperature',
      label: 'Air temperature',
      unit: 'K',
      min: 0.1,
      max: 1000,
      step: 0.1,
    },
    {
      key: 'process_temperature',
      label: 'Process temperature',
      unit: 'K',
      min: 0.1,
      max: 1000,
      step: 0.1,
    },
    {
      key: 'rotational_speed',
      label: 'Rotational speed',
      unit: 'RPM',
      min: 0.1,
      max: 100000,
      step: 1,
    },
    {
      key: 'torque',
      label: 'Torque',
      unit: 'Nm',
      min: 0,
      max: 100000,
      step: 0.1,
    },
    {
      key: 'tool_wear',
      label: 'Tool wear',
      unit: 'min',
      min: 0,
      max: 100000,
      step: 1,
    },
  ]

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">IA</div>
          <div>
            <h1>Industrial AI</h1>
            <p>Intelligence Platform</p>
          </div>
        </div>

        <div className="connection">
          <span className="status-dot" />
          Prediction dashboard
        </div>
      </header>

      <section className="page-heading">
        <p className="eyebrow">MACHINE LEARNING / MONITORING</p>
        <h2>Machine health overview</h2>
        <p>
          Submit machine sensor readings to estimate failure risk
          and review your saved predictions.
        </p>
      </section>

      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}

      <section className="dashboard-grid">
        <div className="panel input-panel">
          <div className="panel-heading">
            <div>
              <h3>Sensor readings</h3>
              <p>Enter the operating conditions.</p>
            </div>
            <span className="panel-number">01</span>
          </div>

          <form onSubmit={submitPrediction}>
            <div className="sensor-grid">
              {fields.map((field) => (
                <label className="field" key={field.key}>
                  <span>{field.label}</span>
                  <div className="input-with-unit">
                    <input
                      type="number"
                      required
                      min={field.min}
                      max={field.max}
                      step={field.step}
                      value={readings[field.key]}
                      onChange={(event) =>
                        updateField(
                          field.key,
                          Number(event.target.value),
                        )
                      }
                    />
                    <span>{field.unit}</span>
                  </div>
                </label>
              ))}
            </div>

            <label className="field product-field">
              <span>Product quality type</span>
              <select
                value={readings.product_type}
                onChange={(event) =>
                  updateField(
                    'product_type',
                    event.target.value as 'L' | 'M' | 'H',
                  )
                }
              >
                <option value="L">L — Low</option>
                <option value="M">M — Medium</option>
                <option value="H">H — High</option>
              </select>
            </label>

            <button
                type="submit"
                className="primary-button"
                disabled={loading}
            >
              {loading
                ? 'Analysing readings...'
                : 'Run failure prediction'}
            </button>

            <p className="form-note">
              Predictions are estimates, not confirmed machine failures.
            </p>
          </form>
        </div>

        <div className="panel result-panel">
          <div className="panel-heading">
            <div>
              <h3>Prediction result</h3>
              <p>Output from the trained ML model.</p>
            </div>
            <span className="panel-number">02</span>
          </div>

          {!result ? (
            <div className="empty-result">
              <div className="empty-icon">↗</div>
              <h4>Ready for analysis</h4>
              <p>
                Submit the sensor readings to see the model's
                failure probability and prediction.
              </p>
            </div>
          ) : (
            <div className="result-content">
              <div className="probability-block">
                <p>Estimated failure probability</p>
                <div className="probability">
                  {(result.failure_probability * 100).toFixed(1)}
                  <span>%</span>
                </div>
                <div className="probability-track">
                  <div
                    className="probability-fill"
                    style={{
                      width: `${result.failure_probability * 100}%`,
                    }}
                  />
                </div>
              </div>

              <div className="result-row">
                <span>Prediction</span>
                <strong>
                  {result.predicted_failure === 1
                    ? 'Potential failure'
                    : 'No failure predicted'}
                </strong>
              </div>

              <div className="result-row">
                <span>Risk category</span>
                <span
                  className={`risk-badge ${result.risk_level.toLowerCase()}`}
                >
                  {result.risk_level}
                </span>
              </div>

              <div className="result-row">
                <span>Decision threshold</span>
                <strong>
                  {(result.decision_threshold * 100).toFixed(1)}%
                </strong>
              </div>

              <div className="result-row">
                <span>Model</span>
                <strong>{result.model_name}</strong>
              </div>

              <p className="form-note">
                Risk categories are illustrative display rules.
                Validate model calibration before operational use.
              </p>
            </div>
          )}
        </div>
      </section>

      
      <section className="analytics-section">
        <div className="analytics-heading">
          <div>
            <p className="eyebrow">PERFORMANCE / INSIGHTS</p>
            <h3>Prediction analytics</h3>
            <p>Summary statistics calculated from saved predictions.</p>
          </div>
          <button
            className="secondary-button"
            onClick={() => void loadAnalytics()}
          >
            Refresh analytics
          </button>
        </div>

        {analyticsError && (
          <div className="error-banner" role="alert">
            {analyticsError}
          </div>
        )}

        {!analytics ? (
          <div className="panel">
            Loading analytics...
          </div>
        ) : (
          <>
            <div className="metric-grid">
              <div className="metric-card">
                <span>Total predictions</span>
                <strong>{analytics.total_predictions}</strong>
                <small>Saved records</small>
              </div>

              <div className="metric-card">
                <span>Predicted failures</span>
                <strong>{analytics.predicted_failures}</strong>
                <small>Model flagged as failure</small>
              </div>

              <div className="metric-card">
                <span>Predicted normal</span>
                <strong>{analytics.predicted_normal}</strong>
                <small>No failure predicted</small>
              </div>

              <div className="metric-card">
                <span>Average failure probability</span>
                <strong>
                  {(analytics.average_failure_probability * 100).toFixed(1)}%
                </strong>
                <small>Across saved predictions</small>
              </div>
            </div>

            <div className="chart-grid">
              <div className="panel chart-panel">
                <div className="panel-heading">
                  <div>
                    <h3>Failure probability over time</h3>
                    <p>Estimated probability for recent saved predictions.</p>
                  </div>
                </div>

                {analytics.recent_predictions.length === 0 ? (
                  <p className="table-message">
                    Submit a prediction to populate this chart.
                  </p>
                ) : (
                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={analytics.recent_predictions.map((item) => ({
                          ...item,
                          probability_percent:
                            item.failure_probability * 100,
                          time: new Date(item.created_at).toLocaleTimeString(),
                        }))}
                      >
                        <CartesianGrid
                          stroke="#29364b"
                          strokeDasharray="3 3"
                        />
                        <XAxis
                          dataKey="id"
                          stroke="#93a4bb"
                          tick={{ fontSize: 11 }}
                          label={{
                            value: 'Prediction ID',
                            position: 'insideBottom',
                            offset: -5,
                            fill: '#93a4bb',
                          }}
                        />
                        <YAxis
                          stroke="#93a4bb"
                          domain={[0, 100]}
                          tick={{ fontSize: 11 }}
                          tickFormatter={(value) => `${value}%`}
                        />
                        <Tooltip
                          contentStyle={{
                            background: '#111a2b',
                            border: '1px solid #35445b',
                            borderRadius: 8,
                          }}
                          labelFormatter={(value) => `Prediction #${value}`}
                          formatter={(value) => [
                            `${Number(value).toFixed(1)}%`,
                            'Failure probability',
                          ]}
                        />
                        <Line
                          type="monotone"
                          dataKey="probability_percent"
                          stroke="#76ddc7"
                          strokeWidth={2}
                          dot={false}
                          activeDot={{ r: 5 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>

              <div className="panel chart-panel">
                <div className="panel-heading">
                  <div>
                    <h3>Risk distribution</h3>
                    <p>Saved predictions grouped by risk category.</p>
                  </div>
                </div>

                {analytics.risk_distribution.length === 0 ? (
                  <p className="table-message">
                    No risk data available yet.
                  </p>
                ) : (
                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={analytics.risk_distribution}
                          dataKey="count"
                          nameKey="risk_level"
                          cx="50%"
                          cy="45%"
                          outerRadius={90}
                          innerRadius={48}
                          paddingAngle={3}
                        >
                          {analytics.risk_distribution.map((item) => (
                            <Cell
                              key={item.risk_level}
                              fill={
                                RISK_COLORS[item.risk_level] ?? '#8ba0bb'
                              }
                            />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{
                            background: '#111a2b',
                            border: '1px solid #35445b',
                            borderRadius: 8,
                          }}
                        />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>

              <div className="panel chart-panel full-width-chart">
                <div className="panel-heading">
                  <div>
                    <h3>Prediction outcomes</h3>
                    <p>Model classifications across stored records.</p>
                  </div>
                </div>

                <div className="chart-container short-chart">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={[
                        {
                          outcome: 'Failure predicted',
                          count: analytics.predicted_failures,
                        },
                        {
                          outcome: 'Normal predicted',
                          count: analytics.predicted_normal,
                        },
                      ]}
                    >
                      <CartesianGrid
                        stroke="#29364b"
                        strokeDasharray="3 3"
                      />
                      <XAxis
                        dataKey="outcome"
                        stroke="#93a4bb"
                        tick={{ fontSize: 11 }}
                      />
                      <YAxis
                        stroke="#93a4bb"
                        allowDecimals={false}
                      />
                      <Tooltip
                        contentStyle={{
                          background: '#111a2b',
                          border: '1px solid #35445b',
                          borderRadius: 8,
                        }}
                      />
                      <Bar
                        dataKey="count"
                        name="Predictions"
                        fill="#76ddc7"
                        radius={[5, 5, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <p className="form-note">
              These charts describe model predictions, not confirmed
              real-world machine failures. Risk categories use the
              illustrative thresholds defined in the prediction engine.
            </p>
          </>
        )}
      </section>


      <section className="panel history-panel">
        <div className="panel-heading">
          <div>
            <h3>Recent predictions</h3>
            <p>Records retrieved from your PostgreSQL database.</p>
          </div>
          <button
            className="secondary-button"
            onClick={() => void loadHistory()}
            disabled={historyLoading}
          >
            Refresh history
          </button>
        </div>

        {historyLoading ? (
          <p className="table-message">Loading prediction history...</p>
        ) : history.length === 0 ? (
          <p className="table-message">
            No saved predictions yet. Submit your first sensor readings.
          </p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Timestamp</th>
                  <th>Failure probability</th>
                  <th>Prediction</th>
                  <th>Risk</th>
                  <th>Model</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={item.id}>
                    <td>#{item.id}</td>
                    <td>
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                    <td>
                      {(item.failure_probability * 100).toFixed(1)}%
                    </td>
                    <td>
                      {item.predicted_failure === 1
                        ? 'Potential failure'
                        : 'No failure predicted'}
                    </td>
                    <td>
                      <span
                        className={`risk-badge ${item.risk_level.toLowerCase()}`}
                      >
                        {item.risk_level}
                      </span>
                    </td>
                    <td>{item.model_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <footer>
        Industrial AI Intelligence Platform
        <span>Educational prototype · Not a safety-critical system</span>
      </footer>
    </main>
  )
}

export default App
