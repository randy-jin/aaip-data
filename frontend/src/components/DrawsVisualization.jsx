import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Bar
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { getDrawStreams, getDrawTrends, getDrawStats, getDrawRecords } from '../api_draws';

export default function DrawsVisualization() {
  const { t } = useTranslation();
  const [streams, setStreams] = useState({ categories: [], streams: [] });
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDetail, setSelectedDetail] = useState('all');
  const [selectedYear, setSelectedYear] = useState('2025');
  const [trendData, setTrendData] = useState([]);
  const [statsData, setStatsData] = useState([]);
  const [recentDraws, setRecentDraws] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStreamsData();
  }, []);

  useEffect(() => {
    if (streams.categories.length > 0) {
      fetchDrawData();
    }
  }, [selectedCategory, selectedDetail, selectedYear, streams]);

  const fetchStreamsData = async () => {
    try {
      const streamsData = await getDrawStreams();
      setStreams(streamsData);
      
      if (streamsData.categories.length > 0) {
        setSelectedCategory('all');
      }
    } catch (err) {
      console.error('Error fetching streams:', err);
      setError(err.message);
    }
  };

  const fetchDrawData = async () => {
    try {
      setLoading(true);
      
      const params = {
        year: parseInt(selectedYear)
      };
      
      if (selectedCategory !== 'all') {
        params.stream_category = selectedCategory;
      }
      
      if (selectedDetail !== 'all') {
        params.stream_detail = selectedDetail;
      }

      const [trends, stats, recent] = await Promise.all([
        getDrawTrends(params),
        getDrawStats(selectedCategory !== 'all' ? selectedCategory : null),
        getDrawRecords({ ...params, limit: 20 })
      ]);

      setTrendData(trends);
      setStatsData(stats);
      setRecentDraws(recent);
      setError(null);
    } catch (err) {
      console.error('Error fetching draw data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
    setSelectedDetail('all');
  };

  const getAvailableDetails = () => {
    if (selectedCategory === 'all') return [];
    return streams.streams
      .filter(s => s.category === selectedCategory)
      .map(s => s.detail);
  };

  const getAvailableYears = () => {
    const currentYear = new Date().getFullYear();
    const years = [];
    for (let year = currentYear; year >= 2024; year--) {
      years.push(year.toString());
    }
    return years;
  };

  const processChartData = () => {
    return trendData.map(item => ({
      date: format(parseISO(item.date), 'MMM dd'),
      fullDate: item.date,
      score: item.min_score,
      invitations: item.invitations,
      stream: `${item.stream_category}${item.stream_detail ? ` - ${item.stream_detail}` : ''}`
    }));
  };

  const chartData = processChartData();

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border border-gray-300 rounded-lg shadow-lg p-3">
          <p className="font-semibold text-gray-900">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading && streams.categories.length === 0) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading draw data...</p>
        </div>
      </div>
    );
  }

  if (error && streams.categories.length === 0) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">Error loading draw data</h3>
        <p className="text-red-600">{error}</p>
        <button
          onClick={fetchStreamsData}
          className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Filter Draw Data</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Stream Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => handleCategoryChange(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              {streams.categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Pathway/Sector</label>
            <select
              value={selectedDetail}
              onChange={(e) => setSelectedDetail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              disabled={selectedCategory === 'all'}
            >
              <option value="all">All Pathways</option>
              {getAvailableDetails().map(detail => (
                <option key={detail} value={detail}>{detail}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Year</label>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {getAvailableYears().map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
        </div>

        {selectedCategory !== 'all' && selectedDetail !== 'all' && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
            <p className="text-sm text-blue-800">
              <span className="font-semibold">Viewing:</span> {selectedCategory} - {selectedDetail} ({selectedYear})
            </p>
          </div>
        )}
      </div>

      {statsData.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Draws"
            value={statsData.reduce((sum, s) => sum + s.total_draws, 0)}
            color="blue"
          />
          <StatCard
            title="Total Invitations"
            value={statsData.reduce((sum, s) => sum + s.total_invitations, 0).toLocaleString()}
            color="green"
          />
          <StatCard
            title="Avg Min Score"
            value={
              statsData.length > 0
                ? Math.round(statsData.reduce((sum, s) => sum + (s.avg_score || 0), 0) / statsData.length)
                : 'N/A'
            }
            color="yellow"
          />
          <StatCard
            title="Score Range"
            value={
              statsData.length > 0
                ? `${Math.min(...statsData.map(s => s.min_score || Infinity))} - ${Math.max(...statsData.map(s => s.max_score || 0))}`
                : 'N/A'
            }
            color="purple"
          />
        </div>
      )}

      {chartData.length > 0 ? (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Minimum Score Trend</h3>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 11 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis label={{ value: 'Min Score', angle: -90, position: 'insideLeft' }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke="#3b82f6" 
                  name="Min Score"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Invitations Issued Trend</h3>
            <ResponsiveContainer width="100%" height={350}>
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 11 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis label={{ value: 'Invitations', angle: -90, position: 'insideLeft' }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Bar 
                  dataKey="invitations" 
                  fill="#10b981" 
                  name="Invitations"
                  radius={[4, 4, 0, 0]}
                />
                <Line 
                  type="monotone" 
                  dataKey="invitations" 
                  stroke="#059669" 
                  strokeWidth={2}
                  dot={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Score vs Invitations</h3>
            <ResponsiveContainer width="100%" height={350}>
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 11 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis yAxisId="left" label={{ value: 'Min Score', angle: -90, position: 'insideLeft' }} />
                <YAxis yAxisId="right" orientation="right" label={{ value: 'Invitations', angle: 90, position: 'insideRight' }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="score" 
                  stroke="#3b82f6" 
                  name="Min Score"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
                <Bar 
                  yAxisId="right"
                  dataKey="invitations" 
                  fill="#10b981" 
                  name="Invitations"
                  opacity={0.6}
                  radius={[4, 4, 0, 0]}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <p className="text-yellow-800">
            No draw data available for the selected filters. Try selecting different options.
          </p>
        </div>
      )}

      {recentDraws.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Recent Draws</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stream</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Detail</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Min Score</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Invitations</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentDraws.map((draw) => (
                  <tr key={draw.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {format(parseISO(draw.draw_date), 'MMM dd, yyyy')}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{draw.stream_category}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{draw.stream_detail || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-blue-600">
                      {draw.min_score || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-green-600">
                      {draw.invitations_issued?.toLocaleString() || 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {statsData.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Stream Statistics</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stream</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Draws</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total Inv.</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Avg Score</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Score Range</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Latest Draw</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {statsData.map((stat, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm">
                      <div className="font-medium text-gray-900">{stat.stream_category}</div>
                      {stat.stream_detail && <div className="text-gray-500 text-xs">{stat.stream_detail}</div>}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">{stat.total_draws}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                      {stat.total_invitations.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-blue-600">
                      {stat.avg_score ? stat.avg_score.toFixed(1) : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                      {stat.min_score || 'N/A'} - {stat.max_score || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {stat.latest_draw_date ? format(parseISO(stat.latest_draw_date), 'MMM dd, yyyy') : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ title, value, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-900',
    green: 'bg-green-50 border-green-200 text-green-900',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    purple: 'bg-purple-50 border-purple-200 text-purple-900',
  };

  return (
    <div className={`${colorClasses[color]} border rounded-lg p-4 shadow-sm`}>
      <h3 className="text-xs font-medium opacity-75 mb-1">{title}</h3>
      <p className="text-2xl font-bold">{value || 'N/A'}</p>
    </div>
  );
}
