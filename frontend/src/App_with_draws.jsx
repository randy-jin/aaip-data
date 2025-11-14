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
import { getStats, getSummaryData } from './api';
import { getDrawStreams, getDrawTrends, getDrawStats, getDrawRecords } from './api_draws';
import DrawsVisualization from './components/DrawsVisualization';

function App() {
  const { t, i18n } = useTranslation();
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('all');
  const [activeTab, setActiveTab] = useState('summary'); // 'summary' or 'draws'

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

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('language', lng);
  };

  const filteredData = filterDataByTimeRange(chartData);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">{t('loading.loadingData')}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h2 className="text-red-800 font-semibold mb-2">{t('error.errorLoadingData')}</h2>
          <p className="text-red-600">{error}</p>
          <button
            onClick={fetchData}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            {t('error.retry')}
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
              <h1 className="text-3xl font-bold text-gray-900">{t('header.title')}</h1>
              <p className="text-sm text-gray-600 mt-1">{t('header.subtitle')}</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => changeLanguage('en')}
                  className={`px-3 py-1 rounded transition ${
                    i18n.language === 'en'
                      ? 'bg-white text-blue-600 shadow'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  EN
                </button>
                <button
                  onClick={() => changeLanguage('zh')}
                  className={`px-3 py-1 rounded transition ${
                    i18n.language === 'zh'
                      ? 'bg-white text-blue-600 shadow'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  中文
                </button>
              </div>
              <button onClick={fetchData} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                {t('header.refresh')}
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Stats Cards */}
        {stats && stats.latest_data && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard title={t('stats.nominationAllocation')} value={stats.latest_data.nomination_allocation?.toLocaleString()} color="blue" />
            <StatCard title={t('stats.nominationsIssued')} value={stats.latest_data.nominations_issued?.toLocaleString()} color="green" />
            <StatCard title={t('stats.spacesRemaining')} value={stats.latest_data.nomination_spaces_remaining?.toLocaleString()} color="yellow" />
            <StatCard title={t('stats.applicationsToProcess')} value={stats.latest_data.applications_to_process?.toLocaleString()} color="purple" />
          </div>
        )}

        {/* Info Banner */}
        {stats && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm text-blue-800">
                  <span className="font-semibold">{t('info.totalRecords')}</span> {stats.total_records} |
                  <span className="font-semibold ml-4">{t('info.lastUpdated')}</span> {stats.latest_data?.last_updated || 'N/A'}
                  {stats.total_draws > 0 && (
                    <span className="ml-4">
                      <span className="font-semibold">{t('info.totalDraws')}</span> {stats.total_draws}
                    </span>
                  )}
                  {stats.latest_draw_date && (
                    <span className="ml-4">
                      <span className="font-semibold">{t('info.latestDrawDate')}</span> {format(parseISO(stats.latest_draw_date), 'MMM dd, yyyy')}
                    </span>
                  )}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('summary')}
                className={`py-4 px-6 text-sm font-medium border-b-2 transition ${
                  activeTab === 'summary'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {t('tabs.nominationSummary')}
              </button>
              <button
                onClick={() => setActiveTab('draws')}
                className={`py-4 px-6 text-sm font-medium border-b-2 transition ${
                  activeTab === 'draws'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {t('tabs.drawHistory')} {stats?.total_draws > 0 && `(${stats.total_draws})`}
              </button>
            </nav>
          </div>
        </div>

        {/* Content based on active tab */}
        {activeTab === 'summary' && (
          <div>
            {/* Time Range Selector */}
            <div className="bg-white rounded-lg shadow p-4 mb-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">{t('timeRange.title')}</h3>
                <div className="flex gap-2">
                  <button onClick={() => setTimeRange('7days')} className={`px-4 py-2 rounded ${timeRange === '7days' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}>
                    {t('timeRange.sevenDays')}
                  </button>
                  <button onClick={() => setTimeRange('30days')} className={`px-4 py-2 rounded ${timeRange === '30days' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}>
                    {t('timeRange.thirtyDays')}
                  </button>
                  <button onClick={() => setTimeRange('all')} className={`px-4 py-2 rounded ${timeRange === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}>
                    {t('timeRange.allTime')}
                  </button>
                </div>
              </div>
            </div>

            {/* Charts */}
            <div className="space-y-8">
              <ChartCard title={t('charts.overallAllocationVsIssued')}>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={filteredData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="allocation" stroke="#3b82f6" name={t('charts.allocation')} strokeWidth={2} />
                    <Line type="monotone" dataKey="issued" stroke="#10b981" name={t('charts.issued')} strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </ChartCard>

              <ChartCard title={t('charts.nominationSpacesRemaining')}>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={filteredData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="remaining" stroke="#f59e0b" name={t('charts.remaining')} strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </ChartCard>

              <ChartCard title={t('charts.applicationsToBProcessed')}>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={filteredData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="applications" stroke="#8b5cf6" name={t('charts.applications')} strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>
          </div>
        )}

        {activeTab === 'draws' && <DrawsVisualization />}

        <footer className="mt-12 text-center text-gray-600 text-sm">
          <p>{t('footer.dataSource')} <a href="https://www.alberta.ca/aaip-processing-information" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Alberta.ca AAIP Processing Information</a></p>
          <p className="mt-2">{t('footer.updateFrequency')}</p>
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
