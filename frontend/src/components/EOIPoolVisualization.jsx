import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { getLatestEOIPool, getEOITrends, getEOIAlerts } from '../api';

function EOIPoolVisualization() {
  const { t } = useTranslation();
  const [latestPool, setLatestPool] = useState([]);
  const [trends, setTrends] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [selectedStream, setSelectedStream] = useState(null);
  const [trendDays, setTrendDays] = useState(7);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedStream || trendDays) {
      fetchTrends();
    }
  }, [selectedStream, trendDays]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [poolData, alertData] = await Promise.all([
        getLatestEOIPool(),
        getEOIAlerts(5.0)
      ]);

      setLatestPool(poolData);
      setAlerts(alertData);

      await fetchTrends();
      setLoading(false);
    } catch (error) {
      console.error('Error fetching EOI data:', error);
      setLoading(false);
    }
  };

  const fetchTrends = async () => {
    try {
      const trendsData = await getEOITrends(selectedStream, trendDays);
      setTrends(trendsData);
    } catch (error) {
      console.error('Error fetching trends:', error);
    }
  };

  const handleRefresh = () => {
    fetchData();
  };

  // Process trend data for charts
  const processTrendData = () => {
    if (!trends || trends.length === 0) return [];

    // Group by stream for multi-line chart
    const streamGroups = {};
    trends.forEach(trend => {
      if (!streamGroups[trend.stream_name]) {
        streamGroups[trend.stream_name] = [];
      }
      streamGroups[trend.stream_name].push({
        ...trend,
        timestamp: format(parseISO(trend.timestamp), 'MMM dd HH:mm')
      });
    });

    // If a specific stream is selected, return its data
    if (selectedStream) {
      return streamGroups[selectedStream] || [];
    }

    // Otherwise, combine all streams into time series
    const timePoints = {};
    trends.forEach(trend => {
      const time = format(parseISO(trend.timestamp), 'MMM dd HH:mm');
      if (!timePoints[time]) {
        timePoints[time] = { time };
      }
      timePoints[time][trend.stream_name] = trend.candidate_count;
    });

    return Object.values(timePoints).reverse();
  };

  const trendChartData = processTrendData();

  // Get unique stream names for the legend
  const streamNames = [...new Set(trends.map(t => t.stream_name))];

  // Colors for different streams
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

  const getAlertBadge = (alertType) => {
    const badges = {
      'significant_increase': 'bg-red-100 text-red-800',
      'significant_decrease': 'bg-green-100 text-green-800',
      'stable': 'bg-gray-100 text-gray-800'
    };
    return badges[alertType] || 'bg-gray-100 text-gray-800';
  };

  const getAlertIcon = (alertType) => {
    if (alertType === 'significant_increase') return '📈';
    if (alertType === 'significant_decrease') return '📉';
    return '➡️';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">{t('loading.loadingData') || 'Loading data...'}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Refresh */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">
          Expression of Interest Pool
        </h2>
        <button
          onClick={handleRefresh}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {t('header.refresh') || 'Refresh Data'}
        </button>
      </div>

      {/* Alerts Section */}
      {alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🔔 Significant Changes (Last Update)
          </h3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {alerts.map((alert, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-2 ${
                  alert.alert_type === 'significant_increase'
                    ? 'border-red-200 bg-red-50'
                    : 'border-green-200 bg-green-50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="font-semibold text-gray-900 text-sm mb-1">
                      {alert.stream_name}
                    </div>
                    <div className="text-2xl font-bold text-gray-900">
                      {alert.current_count.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {getAlertIcon(alert.alert_type)} {alert.change > 0 ? '+' : ''}
                      {alert.change.toLocaleString()} ({alert.change_percentage > 0 ? '+' : ''}
                      {alert.change_percentage.toFixed(1)}%)
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Latest Pool Snapshot */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Current EOI Pool Size
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={latestPool}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="stream_name"
              angle={-45}
              textAnchor="end"
              height={150}
              interval={0}
              tick={{ fontSize: 12 }}
            />
            <YAxis />
            <Tooltip />
            <Bar dataKey="candidate_count" name="Candidates">
              {latestPool.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Trend Controls */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-wrap gap-4 items-center mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Time Period
            </label>
            <select
              value={trendDays}
              onChange={(e) => setTrendDays(Number(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-md"
            >
              <option value={1}>Last 24 Hours</option>
              <option value={3}>Last 3 Days</option>
              <option value={7}>Last 7 Days</option>
              <option value={14}>Last 14 Days</option>
              <option value={30}>Last 30 Days</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Stream Filter
            </label>
            <select
              value={selectedStream || ''}
              onChange={(e) => setSelectedStream(e.target.value || null)}
              className="px-4 py-2 border border-gray-300 rounded-md"
            >
              <option value="">All Streams</option>
              {streamNames.map((name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Trend Chart */}
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          EOI Pool Trends
        </h3>
        {trendChartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={trendChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey={selectedStream ? "timestamp" : "time"}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis />
              <Tooltip />
              <Legend />
              {selectedStream ? (
                <Line
                  type="monotone"
                  dataKey="candidate_count"
                  stroke={colors[0]}
                  strokeWidth={2}
                  name={selectedStream}
                  dot={{ r: 4 }}
                />
              ) : (
                streamNames.map((name, index) => (
                  <Line
                    key={name}
                    type="monotone"
                    dataKey={name}
                    stroke={colors[index % colors.length]}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                ))
              )}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center text-gray-500 py-8">
            No trend data available for the selected period
          </div>
        )}
      </div>

      {/* Data Table */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Latest Pool Data
        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Stream / Pathway
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Candidates in Pool
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Last Updated
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {latestPool.map((pool, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {pool.stream_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {pool.candidate_count.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {pool.last_updated || 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default EOIPoolVisualization;
