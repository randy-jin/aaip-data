import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  UserGroupIcon,
  BanknotesIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline';

const AlbertaEconomyIndicators = () => {
  const { t, i18n } = useTranslation();
  const [economyData, setEconomyData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEconomyData();
  }, []);

  const fetchEconomyData = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/alberta-economy/indicators`
      );
      if (response.ok) {
        const data = await response.json();
        setEconomyData(data);
      }
    } catch (err) {
      console.error('Error fetching economy data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getIndicatorColor = (type) => {
    if (type === 'positive') return 'text-green-600';
    if (type === 'neutral') return 'text-blue-600';
    if (type === 'caution') return 'text-amber-600';
    return 'text-gray-600';
  };

  const getIndicatorIcon = (type) => {
    if (type === 'positive') return '🟢';
    if (type === 'neutral') return '🔵';
    if (type === 'caution') return '🟡';
    return '⚪';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!economyData?.current) {
    return null;
  }

  const { current } = economyData;

  return (
    <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg shadow-md p-6 border border-indigo-100">
      {/* Header */}
      <div className="flex items-center gap-2 mb-6">
        <ChartBarIcon className="h-6 w-6 text-indigo-600" />
        <h3 className="text-xl font-bold text-gray-900">
          {i18n.language === 'zh' ? '阿尔伯塔省经济指标' : 'Alberta Economic Indicators'}
        </h3>
      </div>

      {/* Key Indicators Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {/* Unemployment Rate */}
        {current.unemployment_rate && (
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <UserGroupIcon className="h-5 w-5 text-gray-500" />
              <span className="text-xs text-gray-600 font-medium">
                {i18n.language === 'zh' ? '失业率' : 'Unemployment'}
              </span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {current.unemployment_rate}%
            </div>
            {current.unemployment_rate < 6.5 ? (
              <div className="text-xs text-green-600 mt-1">
                {i18n.language === 'zh' ? '低' : 'Low'}
              </div>
            ) : (
              <div className="text-xs text-gray-600 mt-1">
                {i18n.language === 'zh' ? '适中' : 'Moderate'}
              </div>
            )}
          </div>
        )}

        {/* GDP Growth */}
        {current.gdp_growth && (
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <ArrowTrendingUpIcon className="h-5 w-5 text-gray-500" />
              <span className="text-xs text-gray-600 font-medium">
                {i18n.language === 'zh' ? 'GDP增长' : 'GDP Growth'}
              </span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {current.gdp_growth}%
            </div>
            {current.gdp_growth > 2.5 ? (
              <div className="text-xs text-green-600 mt-1">
                {i18n.language === 'zh' ? '强劲' : 'Strong'}
              </div>
            ) : (
              <div className="text-xs text-gray-600 mt-1">
                {i18n.language === 'zh' ? '稳定' : 'Steady'}
              </div>
            )}
          </div>
        )}

        {/* Population Growth */}
        {current.population_growth && (
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <BuildingOfficeIcon className="h-5 w-5 text-gray-500" />
              <span className="text-xs text-gray-600 font-medium">
                {i18n.language === 'zh' ? '人口增长' : 'Population'}
              </span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {current.population_growth}%
            </div>
            <div className="text-xs text-green-600 mt-1">
              {i18n.language === 'zh' ? '快速' : 'Rapid'}
            </div>
          </div>
        )}

        {/* Oil Price */}
        {current.oil_price && (
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <BanknotesIcon className="h-5 w-5 text-gray-500" />
              <span className="text-xs text-gray-600 font-medium">
                {i18n.language === 'zh' ? '油价 (WTI)' : 'Oil Price (WTI)'}
              </span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              ${current.oil_price}
            </div>
            <div className="text-xs text-gray-600 mt-1">
              {current.oil_price_trend === 'up' && (i18n.language === 'zh' ? '上涨' : 'Rising')}
              {current.oil_price_trend === 'down' && (i18n.language === 'zh' ? '下降' : 'Falling')}
              {current.oil_price_trend === 'stable' && (i18n.language === 'zh' ? '稳定' : 'Stable')}
            </div>
          </div>
        )}
      </div>

      {/* Economic Insights */}
      {current.insights && current.insights.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">
            {i18n.language === 'zh' ? '经济洞察与AAIP影响' : 'Economic Insights & AAIP Impact'}
          </h4>
          
          {current.insights.map((insight, index) => (
            <div
              key={index}
              className="bg-white border-l-4 border-indigo-400 rounded-r-lg p-4"
            >
              <div className="flex items-start gap-3">
                <span className="text-xl">{getIndicatorIcon(insight.type)}</span>
                <div className="flex-1">
                  <div className={`font-medium text-sm mb-1 ${getIndicatorColor(insight.type)}`}>
                    {insight.indicator}
                  </div>
                  <p className="text-sm text-gray-700 mb-2">
                    {insight.message}
                  </p>
                  <div className="bg-indigo-50 rounded px-3 py-2 text-xs text-indigo-800">
                    <strong>{i18n.language === 'zh' ? 'AAIP影响：' : 'AAIP Impact: '}</strong>
                    {insight.aaip_impact}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Data timestamp */}
      {current.timestamp && (
        <div className="mt-4 pt-4 border-t border-indigo-200">
          <p className="text-xs text-gray-500 text-center">
            {i18n.language === 'zh' ? '数据更新时间：' : 'Data updated: '}
            {new Date(current.timestamp).toLocaleDateString(i18n.language === 'zh' ? 'zh-CN' : 'en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </p>
        </div>
      )}
    </div>
  );
};

export default AlbertaEconomyIndicators;
