import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  CalculatorIcon,
  ClockIcon,
  ChartBarIcon,
  CalendarIcon
} from '@heroicons/react/24/outline';

const ToolsDashboard = () => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('quota');
  const [quotaData, setQuotaData] = useState([]);
  const [processingData, setProcessingData] = useState([]);
  const [competitivenessData, setCompetitivenessData] = useState([]);
  const [submissionDate, setSubmissionDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 'quota') {
      fetchQuotaCalculation();
    } else if (activeTab === 'competitiveness') {
      fetchCompetitiveness();
    }
  }, [activeTab]);

  const fetchQuotaCalculation = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/tools/quota-calculator`);
      const data = await response.json();
      setQuotaData(data);
    } catch (err) {
      console.error('Error fetching quota data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProcessingTimeline = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/tools/processing-timeline?submission_date=${submissionDate}`
      );
      const data = await response.json();
      setProcessingData(data);
    } catch (err) {
      console.error('Error fetching processing data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCompetitiveness = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/tools/competitiveness`);
      const data = await response.json();
      setCompetitivenessData(data);
    } catch (err) {
      console.error('Error fetching competitiveness data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getWarningColor = (level) => {
    switch (level) {
      case 'critical':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'warning':
        return 'text-amber-600 bg-amber-50 border-amber-200';
      default:
        return 'text-green-600 bg-green-50 border-green-200';
    }
  };

  const getCompetitivenessColor = (level) => {
    switch (level) {
      case 'Very High':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'High':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'Medium':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-green-100 text-green-800 border-green-300';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <CalculatorIcon className="h-7 w-7 text-indigo-600" />
        {t('tools.title', 'Planning Tools')}
      </h2>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('quota')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'quota'
              ? 'text-indigo-600 border-b-2 border-indigo-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <div className="flex items-center gap-2">
            <ChartBarIcon className="h-5 w-5" />
            {t('tools.quotaCalculator', 'Quota Calculator')}
          </div>
        </button>
        <button
          onClick={() => setActiveTab('processing')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'processing'
              ? 'text-indigo-600 border-b-2 border-indigo-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <div className="flex items-center gap-2">
            <ClockIcon className="h-5 w-5" />
            {t('tools.processingTimeline', 'Processing Timeline')}
          </div>
        </button>
        <button
          onClick={() => setActiveTab('competitiveness')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'competitiveness'
              ? 'text-indigo-600 border-b-2 border-indigo-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <div className="flex items-center gap-2">
            <ChartBarIcon className="h-5 w-5" />
            {t('tools.competitiveness', 'Competitiveness')}
          </div>
        </button>
      </div>

      {/* Quota Calculator Tab */}
      {activeTab === 'quota' && (
        <div className="space-y-4">
          <p className="text-gray-600 text-sm mb-4">
            {t('tools.quotaDesc', 'Estimated quota exhaustion dates based on historical usage rates')}
          </p>
          {loading ? (
            <div className="animate-pulse space-y-3">
              {[1, 2, 3].map(i => <div key={i} className="h-24 bg-gray-200 rounded" />)}
            </div>
          ) : (
            quotaData.map((stream, index) => (
              <div key={index} className={`border rounded-lg p-4 ${getWarningColor(stream.warning_level)}`}>
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-lg">{stream.stream_name}</h3>
                  <span className={`px-2 py-1 rounded text-xs font-medium border ${getWarningColor(stream.warning_level)}`}>
                    {stream.warning_level === 'critical' ? '🔴 Critical' : 
                     stream.warning_level === 'warning' ? '🟡 Warning' : '🟢 Normal'}
                  </span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">{t('tools.remaining', 'Remaining')}</p>
                    <p className="font-bold text-lg">{stream.current_remaining}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">{t('tools.usageRate', 'Usage Rate')}</p>
                    <p className="font-bold text-lg">{stream.usage_rate_per_day.toFixed(1)}/day</p>
                  </div>
                  <div>
                    <p className="text-gray-600">{t('tools.daysToExhaust', 'Days to Exhaust')}</p>
                    <p className="font-bold text-lg">
                      {stream.estimated_days_to_exhaust || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">{t('tools.estimatedDate', 'Est. Date')}</p>
                    <p className="font-bold text-lg">
                      {stream.estimated_exhaustion_date 
                        ? new Date(stream.estimated_exhaustion_date).toLocaleDateString()
                        : 'N/A'}
                    </p>
                  </div>
                </div>
                <div className="mt-3 text-xs text-gray-600">
                  {t('tools.confidence', 'Confidence')}: {stream.confidence_level}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Processing Timeline Tab */}
      {activeTab === 'processing' && (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <label className="block text-sm font-medium mb-2 flex items-center gap-2">
              <CalendarIcon className="h-5 w-5 text-blue-600" />
              {t('tools.yourSubmissionDate', 'Your Submission Date')}
            </label>
            <div className="flex gap-2">
              <input
                type="date"
                value={submissionDate}
                onChange={(e) => setSubmissionDate(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
              />
              <button
                onClick={fetchProcessingTimeline}
                className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
              >
                {t('tools.calculate', 'Calculate')}
              </button>
            </div>
          </div>

          {loading ? (
            <div className="animate-pulse space-y-3">
              {[1, 2, 3].map(i => <div key={i} className="h-32 bg-gray-200 rounded" />)}
            </div>
          ) : processingData.length > 0 ? (
            processingData.map((stream, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                <h3 className="font-semibold text-lg mb-3">{stream.stream_name}</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">{t('tools.currentProcessing', 'Current Processing Date')}:</span>
                    <span className="font-medium">{stream.current_processing_date || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">{t('tools.estimatedWait', 'Estimated Wait')}:</span>
                    <span className="font-medium">
                      {stream.estimated_wait_months 
                        ? `~${stream.estimated_wait_months} months`
                        : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">{t('tools.estimatedProcessing', 'Est. Processing Date')}:</span>
                    <span className="font-medium">
                      {stream.estimated_processing_date
                        ? new Date(stream.estimated_processing_date).toLocaleDateString()
                        : 'N/A'}
                    </span>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-gray-300 text-xs text-gray-600 italic">
                  {stream.notes}
                </div>
              </div>
            ))
          ) : (
            <p className="text-center text-gray-500 py-8">
              {t('tools.enterDate', 'Enter your submission date and click Calculate')}
            </p>
          )}
        </div>
      )}

      {/* Competitiveness Tab */}
      {activeTab === 'competitiveness' && (
        <div className="space-y-4">
          <p className="text-gray-600 text-sm mb-4">
            {t('tools.competitivenessDesc', 'Current competition level for each stream based on quota usage, pool size, and application volume')}
          </p>
          {loading ? (
            <div className="animate-pulse space-y-3">
              {[1, 2, 3].map(i => <div key={i} className="h-32 bg-gray-200 rounded" />)}
            </div>
          ) : (
            competitivenessData.map((stream, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 bg-white">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-lg">{stream.stream_name}</h3>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getCompetitivenessColor(stream.level)}`}>
                    {stream.level}
                  </span>
                </div>
                
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span>{t('tools.competitivenessScore', 'Score')}</span>
                    <span className="font-bold">{stream.competitiveness_score}/100</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        stream.competitiveness_score >= 80 ? 'bg-red-500' :
                        stream.competitiveness_score >= 65 ? 'bg-amber-500' :
                        stream.competitiveness_score >= 50 ? 'bg-blue-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${stream.competitiveness_score}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-2 text-sm mb-3">
                  {Object.entries(stream.factors).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-gray-700">
                      <span className="capitalize">{key.replace(/_/g, ' ')}:</span>
                      <span className="font-medium">{value}</span>
                    </div>
                  ))}
                </div>

                <div className="mt-3 pt-3 border-t border-gray-200 bg-blue-50 rounded p-3 text-sm">
                  <p className="font-medium text-blue-900 mb-1">
                    💡 {t('tools.recommendation', 'Recommendation')}
                  </p>
                  <p className="text-blue-800">{stream.recommendation}</p>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      <div className="mt-6 pt-4 border-t border-gray-200 text-xs text-gray-500">
        <p>
          {t('tools.disclaimer', 'All calculations are based on historical data and current trends. Actual results may vary due to policy changes or other factors.')}
        </p>
      </div>
    </div>
  );
};

export default ToolsDashboard;
