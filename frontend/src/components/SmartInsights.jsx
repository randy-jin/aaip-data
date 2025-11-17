import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  ExclamationTriangleIcon, 
  LightBulbIcon, 
  CheckCircleIcon,
  InformationCircleIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

const SmartInsights = () => {
  const { t } = useTranslation();
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchInsights();
    // Refresh insights every 5 minutes
    const interval = setInterval(fetchInsights, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchInsights = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/insights/weekly`);
      if (!response.ok) throw new Error('Failed to fetch insights');
      const data = await response.json();
      setInsights(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching insights:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'warning':
        return <ExclamationTriangleIcon className="h-6 w-6 text-amber-500" />;
      case 'opportunity':
        return <LightBulbIcon className="h-6 w-6 text-blue-500" />;
      case 'positive':
        return <CheckCircleIcon className="h-6 w-6 text-green-500" />;
      default:
        return <InformationCircleIcon className="h-6 w-6 text-gray-500" />;
    }
  };

  const getBackgroundColor = (type) => {
    switch (type) {
      case 'warning':
        return 'bg-amber-50 border-amber-200';
      case 'opportunity':
        return 'bg-blue-50 border-blue-200';
      case 'positive':
        return 'bg-green-50 border-green-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-2 mb-4">
          <SparklesIcon className="h-6 w-6 text-purple-500" />
          <h2 className="text-xl font-bold">{t('smartInsights.title', 'Smart Insights')}</h2>
        </div>
        <div className="animate-pulse space-y-4">
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-2 mb-4">
          <SparklesIcon className="h-6 w-6 text-purple-500" />
          <h2 className="text-xl font-bold">{t('smartInsights.title', 'Smart Insights')}</h2>
        </div>
        <p className="text-red-500">{t('smartInsights.error', 'Failed to load insights')}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center gap-2 mb-6">
        <SparklesIcon className="h-6 w-6 text-purple-500" />
        <h2 className="text-xl font-bold">{t('smartInsights.title', 'Smart Insights')}</h2>
        <span className="ml-auto text-sm text-gray-500">
          {t('smartInsights.updated', 'Auto-updated')}
        </span>
      </div>

      {insights.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <InformationCircleIcon className="h-12 w-12 mx-auto mb-2 opacity-50" />
          <p>{t('smartInsights.noInsights', 'No significant insights at this time. Check back later!')}</p>
        </div>
      ) : (
        <div className="space-y-4">
          {insights.map((insight, index) => (
            <div
              key={index}
              className={`border rounded-lg p-4 ${getBackgroundColor(insight.type)}`}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-1">
                  {getIcon(insight.type)}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">
                    {insight.title}
                  </h3>
                  <p className="text-gray-700 text-sm mb-2">
                    {insight.detail}
                  </p>
                  {insight.reasoning && (
                    <p className="text-gray-600 text-xs italic mb-2">
                      💡 {insight.reasoning}
                    </p>
                  )}
                  {insight.action && (
                    <div className="mt-2 p-2 bg-white bg-opacity-70 rounded border border-current border-opacity-20">
                      <p className="text-sm font-medium text-gray-800">
                        ✨ {t('smartInsights.recommendation', 'Recommendation')}: {insight.action}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-6 pt-4 border-t border-gray-200 text-xs text-gray-500">
        <p>
          {t('smartInsights.disclaimer', 'These insights are generated based on historical data patterns and are for informational purposes only. Immigration policies may change without notice.')}
        </p>
      </div>
    </div>
  );
};

export default SmartInsights;
