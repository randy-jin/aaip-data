import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  BriefcaseIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ArrowPathIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

const LaborMarketInsights = () => {
  const { t } = useTranslation();
  const [insights, setInsights] = useState([]);
  const [occupations, setOccupations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
    // Refresh every 12 hours (labor market data doesn't change frequently)
    const interval = setInterval(fetchData, 12 * 60 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [insightsRes, occupationsRes] = await Promise.all([
        fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/job-bank/insights`),
        fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/job-bank/occupations`)
      ]);

      if (insightsRes.ok) {
        const insightsData = await insightsRes.json();
        setInsights(insightsData);
      }

      if (occupationsRes.ok) {
        const occupationsData = await occupationsRes.json();
        setOccupations(occupationsData);
      }

      setError(null);
    } catch (err) {
      console.error('Error fetching labor market data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getInsightIcon = (type) => {
    switch (type) {
      case 'growth':
        return <ArrowTrendingUpIcon className="h-6 w-6 text-green-500" />;
      case 'decline':
        return <ArrowTrendingDownIcon className="h-6 w-6 text-red-500" />;
      case 'high_demand':
        return <ChartBarIcon className="h-6 w-6 text-blue-500" />;
      default:
        return <ArrowPathIcon className="h-6 w-6 text-gray-500" />;
    }
  };

  const getInsightColor = (type) => {
    switch (type) {
      case 'growth':
      case 'high_demand':
        return 'bg-green-50 border-green-200';
      case 'decline':
        return 'bg-amber-50 border-amber-200';
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  const getOutlookBadge = (outlook) => {
    const colors = {
      'Good': 'bg-green-100 text-green-800 border-green-300',
      'Fair': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'Limited': 'bg-red-100 text-red-800 border-red-300'
    };
    return colors[outlook] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-2 mb-4">
          <BriefcaseIcon className="h-6 w-6 text-indigo-600" />
          <h2 className="text-xl font-bold">{t('laborMarket.title', 'Labor Market Insights')}</h2>
        </div>
        <div className="animate-pulse space-y-4">
          <div className="h-24 bg-gray-200 rounded"></div>
          <div className="h-24 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-2 mb-4">
          <BriefcaseIcon className="h-6 w-6 text-indigo-600" />
          <h2 className="text-xl font-bold">{t('laborMarket.title', 'Labor Market Insights')}</h2>
        </div>
        <p className="text-red-500">{t('laborMarket.error', 'Failed to load labor market data')}</p>
      </div>
    );
  }

  const noData = insights.length === 0 && occupations.length === 0;

  if (noData) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-2 mb-4">
          <BriefcaseIcon className="h-6 w-6 text-indigo-600" />
          <h2 className="text-xl font-bold">{t('laborMarket.title', 'Labor Market Insights')}</h2>
        </div>
        <div className="text-center py-8">
          <BriefcaseIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600">
            {t('laborMarket.noData', 'Labor market data will be available after the first scraping run.')}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            {t('laborMarket.dataSource', 'Data source: Job Bank Canada')}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Labor Market Insights */}
      {insights.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center gap-2 mb-6">
            <BriefcaseIcon className="h-6 w-6 text-indigo-600" />
            <h2 className="text-xl font-bold">
              {t('laborMarket.insights', 'Labor Market Insights')}
            </h2>
            <span className="ml-auto text-sm text-gray-500">
              {t('laborMarket.source', 'Based on Job Bank data')}
            </span>
          </div>

          <div className="space-y-4">
            {insights.map((insight, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${getInsightColor(insight.insight_type)}`}
              >
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-1">
                    {getInsightIcon(insight.insight_type)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-gray-900">
                        {insight.stream_affected}
                      </h3>
                      <span className="px-2 py-1 bg-white bg-opacity-70 rounded text-xs font-medium text-gray-700">
                        {insight.occupation_category}
                      </span>
                    </div>
                    <p className="text-gray-800 mb-2">
                      <strong>{t('laborMarket.trend', 'Trend')}:</strong> {insight.trend_description}
                    </p>
                    <p className="text-gray-700 text-sm mb-2">
                      <strong>{t('laborMarket.impact', 'Impact')}:</strong> {insight.impact_analysis}
                    </p>
                    {insight.recommendation && (
                      <div className="mt-2 p-2 bg-white bg-opacity-70 rounded border border-current border-opacity-20">
                        <p className="text-sm font-medium text-gray-800">
                          💡 {insight.recommendation}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Occupation Details */}
      {occupations.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold mb-6">
            {t('laborMarket.occupations', 'Tracked Occupations')}
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {occupations.map((occ, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-gray-900 text-sm">{occ.occupation_title}</h3>
                  {occ.outlook && (
                    <span className={`px-2 py-1 rounded text-xs font-medium border ${getOutlookBadge(occ.outlook)}`}>
                      {occ.outlook}
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-600 mb-3">NOC {occ.noc_code}</p>
                
                <div className="space-y-1 text-sm">
                  {occ.job_openings !== null && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">{t('laborMarket.openings', 'Job Openings')}:</span>
                      <span className="font-medium">{occ.job_openings.toLocaleString()}</span>
                    </div>
                  )}
                  {occ.job_seekers !== null && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">{t('laborMarket.seekers', 'Job Seekers')}:</span>
                      <span className="font-medium">{occ.job_seekers.toLocaleString()}</span>
                    </div>
                  )}
                  {occ.median_wage !== null && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">{t('laborMarket.wage', 'Median Wage')}:</span>
                      <span className="font-medium">${occ.median_wage.toFixed(2)}/hr</span>
                    </div>
                  )}
                </div>

                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-xs text-indigo-600 font-medium">
                    {t('laborMarket.relatedTo', 'Related to')}: {occ.aaip_stream}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Disclaimer */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-gray-700">
        <p className="font-medium mb-1">ℹ️ {t('laborMarket.about', 'About This Data')}</p>
        <p>
          {t('laborMarket.disclaimer', 'Labor market data is sourced from Job Bank Canada and reflects general employment trends in Alberta. This data provides context for understanding AAIP stream priorities but does not guarantee nomination outcomes.')}
        </p>
      </div>
    </div>
  );
};

export default LaborMarketInsights;
