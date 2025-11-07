import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';
import { getStats, getSummaryData } from './api';

function App() {
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('all');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statsData, summaryData] = await Promise.all([
        getStats(),
        getSummaryData(1000, 0)
      ]);
      
      setStats(statsData);
      
      const processed = summaryData.reverse().map(item => ({
        timestamp: item.timestamp,
        date: format(parseISO(item.timestamp), 'MMM dd HH:mm'),
        allocation: item.nomination_allocation,
        issued: item.nominations_issued,
        remaining: item.nomination_spaces_remaining,
        applications: item.applications_to_process
      }));
      
      setChartData(processed);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to fetch data');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterDataByTimeRange = (data) => {
    if (timeRange === 'all') return data;
    
    const now = new Date();
    const days = timeRange === '7days' ? 7 : 30;
    const cutoff = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
    
    return data.filter(item => new Date(item.timestamp) >= cutoff);
  };

  const filteredData = filterDataByTimeRange(chartData);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h2 className="text-red-800 font-semibold mb-2">Error Loading Data</h2>
          <p className="text-red-600">{error}</p>
          <button 
            onClick={fetchData}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">AAIP Data Tracker</h1>
              <p className="text-sm text-gray-600 mt-1">Alberta Advantage Immigration Program Processing Information</p>
            </div>
            <button onClick={fetchData} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
              Refresh Data
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {stats && stats.latest_data && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard title="Nomination Allocation" value={stats.latest_data.nomination_allocation?.toLocaleString()} color="blue" />
            <StatCard title="Nominations Issued" value={stats.latest_data.nominations_issued?.toLocaleString()} color="green" />
            <StatCard title="Spaces Remaining" value={stats.latest_data.nomination_spaces_remaining?.toLocaleString()} color="yellow" />
            <StatCard title="Applications to Process" value={stats.latest_data.applications_to_process?.toLocaleString()} color="purple" />
          </div>
        )}

        {stats && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
            <div className="flex items-start">
              <div className="flex-1">
                <p className="text-sm text-blue-800">
                  <span className="font-semibold">Total Records:</span> {stats.total_records} | 
                  <span className="font-semibold ml-4">Last Updated:</span> {stats.latest_data?.last_updated || 'N/A'}
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Trend Analysis</h2>
            <div className="flex gap-2">
              <button onClick={() => setTimeRange('7days')} className={`px-4 py-2 rounded ${timeRange === '7days' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}>7 Days</button>
              <button onClick={() => setTimeRange('30days')} className={`px-4 py-2 rounded ${timeRange === '30days' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}>30 Days</button>
              <button onClick={() => setTimeRange('all')} className={`px-4 py-2 rounded ${timeRange === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}>All Time</button>
            </div>
          </div>
        </div>

        <div className="space-y-8">
          <ChartCard title="2025 Nomination Allocation vs Issued">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={filteredData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="allocation" stroke="#3b82f6" name="Allocation" strokeWidth={2} />
                <Line type="monotone" dataKey="issued" stroke="#10b981" name="Issued" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Nomination Spaces Remaining">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={filteredData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="remaining" stroke="#f59e0b" name="Remaining" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Applications to be Processed">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={filteredData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="applications" stroke="#8b5cf6" name="Applications" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="All Metrics Overview">
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={filteredData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="allocation" stroke="#3b82f6" name="Allocation" strokeWidth={2} />
                <Line type="monotone" dataKey="issued" stroke="#10b981" name="Issued" strokeWidth={2} />
                <Line type="monotone" dataKey="remaining" stroke="#f59e0b" name="Remaining" strokeWidth={2} />
                <Line type="monotone" dataKey="applications" stroke="#8b5cf6" name="Applications" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        <footer className="mt-12 text-center text-gray-600 text-sm">
          <p>Data source: <a href="https://www.alberta.ca/aaip-processing-information" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Alberta.ca AAIP Processing Information</a></p>
          <p className="mt-2">Data is collected and updated every hour</p>
        </footer>
      </main>
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
    <div className={`${colorClasses[color]} border rounded-lg p-6 shadow-sm`}>
      <h3 className="text-sm font-medium opacity-75 mb-2">{title}</h3>
      <p className="text-3xl font-bold">{value || 'N/A'}</p>
    </div>
  );
}

function ChartCard({ title, children }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      {children}
    </div>
  );
}

export default App;
