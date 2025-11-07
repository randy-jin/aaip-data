import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';
import { getStats, getSummaryData, getStreamList, getStreamData } from './api';

function App() {
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [streamList, setStreamList] = useState([]);
  const [selectedStream, setSelectedStream] = useState('overall');
  const [streamChartData, setStreamChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('all');

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedStream !== 'overall' && streamList.length > 0) {
      fetchStreamData(selectedStream);
    }
  }, [selectedStream, streamList]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [statsData, summaryData] = await Promise.all([
        getStats(),
        getSummaryData(1000, 0)
      ]);
      
      setStats(statsData);
      
      // Process overall summary data with error handling
      if (Array.isArray(summaryData) && summaryData.length > 0) {
        const processed = summaryData.reverse().map(item => {
          try {
            return {
              timestamp: item.timestamp,
              date: format(parseISO(item.timestamp), 'MMM dd HH:mm'),
              allocation: item.nomination_allocation || 0,
              issued: item.nominations_issued || 0,
              remaining: item.nomination_spaces_remaining || 0,
              applications: item.applications_to_process || 0
            };
          } catch (e) {
            console.error('Error processing item:', item, e);
            return null;
          }
        }).filter(item => item !== null);
        
        setChartData(processed);
      } else {
        setChartData([]);
      }
      
      // Fetch stream list if available
      try {
        const streams = await getStreamList();
        if (streams && Array.isArray(streams.streams)) {
          setStreamList(streams.streams);
        } else {
          setStreamList([]);
        }
      } catch (err) {
        console.log('Stream data not available yet:', err.message);
        setStreamList([]);
      }
      
    } catch (err) {
      setError(err.message || 'Failed to fetch data');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStreamData = async (streamName) => {
    try {
      const data = await getStreamData(streamName, 1000);
      if (Array.isArray(data) && data.length > 0) {
        const processed = data.reverse().map(item => {
          try {
            return {
              timestamp: item.timestamp,
              date: format(parseISO(item.timestamp), 'MMM dd HH:mm'),
              allocation: item.nomination_allocation || 0,
              issued: item.nominations_issued || 0,
              remaining: item.nomination_spaces_remaining || 0,
              applications: item.applications_to_process || 0
            };
          } catch (e) {
            console.error('Error processing stream item:', item, e);
            return null;
          }
        }).filter(item => item !== null);
        setStreamChartData(processed);
      } else {
        setStreamChartData([]);
      }
    } catch (err) {
      console.error('Error fetching stream data:', err);
      setStreamChartData([]);
    }
  };

  const filterDataByTimeRange = (data) => {
    if (!Array.isArray(data) || data.length === 0) return [];
    if (timeRange === 'all') return data;
    
    try {
      const now = new Date();
      const days = timeRange === '7days' ? 7 : 30;
      const cutoff = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
      
      return data.filter(item => {
        try {
          return new Date(item.timestamp) >= cutoff;
        } catch (e) {
          return false;
        }
      });
    } catch (e) {
      console.error('Error filtering data:', e);
      return data;
    }
  };

  const currentData = selectedStream === 'overall' ? chartData : streamChartData;
  const filteredData = filterDataByTimeRange(currentData);

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

  const hasData = filteredData && filteredData.length > 0;

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
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm text-blue-800">
                  <span className="font-semibold">Total Records:</span> {stats.total_records} | 
                  <span className="font-semibold ml-4">Last Updated:</span> {stats.latest_data?.last_updated || 'N/A'}
                  {stats.total_streams > 0 && (
                    <span className="ml-4">
                      <span className="font-semibold">Streams Tracked:</span> {stats.total_streams}
                    </span>
                  )}
                </p>
              </div>
            </div>
          </div>
        )}

        {streamList.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex-1 min-w-[200px]">
                <label htmlFor="stream-select" className="block text-sm font-medium text-gray-700 mb-2">
                  Select Stream:
                </label>
                <select
                  id="stream-select"
                  value={selectedStream}
                  onChange={(e) => setSelectedStream(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="overall">Overall Summary (All Streams)</option>
                  <optgroup label="Main Streams">
                    {streamList.filter(s => s.stream_type === 'main').map(stream => (
                        <option key={stream.stream_name} value={stream.stream_name}>{stream.stream_name}</option>
                      ))}
                  </optgroup>
                  <optgroup label="Express Entry Pathways">
                    {streamList.filter(s => s.stream_type === 'sub-pathway').map(stream => (
                        <option key={stream.stream_name} value={stream.stream_name}>{stream.stream_name}</option>
                      ))}
                  </optgroup>
                </select>
              </div>
              <div className="flex gap-2">
                <button onClick={() => setTimeRange('7days')} className={`px-4 py-2 rounded ${timeRange === '7days' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}>7 Days</button>
                <button onClick={() => setTimeRange('30days')} className={`px-4 py-2 rounded ${timeRange === '30days' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}>30 Days</button>
                <button onClick={() => setTimeRange('all')} className={`px-4 py-2 rounded ${timeRange === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}>All Time</button>
              </div>
            </div>
            {selectedStream !== 'overall' && (
              <div className="mt-4 text-sm text-gray-600">
                <span className="font-semibold">Viewing:</span> {selectedStream}
                {streamChartData.length > 0 && (
                  <span className="ml-4"><span className="font-semibold">Data Points:</span> {streamChartData.length}</span>
                )}
              </div>
            )}
          </div>
        )}

        {!hasData && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8">
            <p className="text-yellow-800">
              <span className="font-semibold">No data available yet.</span> 
              {selectedStream !== 'overall' ? ' Try selecting "Overall Summary" or wait for data collection.' : ' Please run the scraper to collect data.'}
            </p>
          </div>
        )}

        {hasData && (
          <div className="space-y-8">
            <ChartCard title={selectedStream === 'overall' ? '2025 Overall Allocation vs Issued' : `${selectedStream} - Allocation vs Issued`}>
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

            <ChartCard title={selectedStream === 'overall' ? 'Nomination Spaces Remaining' : `${selectedStream} - Spaces Remaining`}>
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

            <ChartCard title={selectedStream === 'overall' ? 'Applications to be Processed' : `${selectedStream} - Applications to Process`}>
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

            <ChartCard title={selectedStream === 'overall' ? 'All Metrics Overview' : `${selectedStream} - All Metrics`}>
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
        )}

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
