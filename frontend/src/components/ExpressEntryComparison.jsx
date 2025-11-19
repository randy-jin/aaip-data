import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  ArrowsRightLeftIcon,
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  TrophyIcon
} from '@heroicons/react/24/outline';

const ExpressEntryComparison = () => {
  const { t, i18n } = useTranslation();
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchComparisonData();
  }, []);

  const fetchComparisonData = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/express-entry/comparison`
      );
      if (response.ok) {
        const data = await response.json();
        setComparisonData(data);
      }
    } catch (err) {
      console.error('Error fetching comparison data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="grid grid-cols-2 gap-4">
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!comparisonData?.comparison) {
    return null;
  }

  const { comparison, insights, express_entry, aaip } = comparisonData;

  return (
    <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg shadow-md p-6 border border-purple-100">
      {/* Header */}
      <div className="flex items-center gap-2 mb-6">
        <ArrowsRightLeftIcon className="h-6 w-6 text-purple-600" />
        <h3 className="text-xl font-bold text-gray-900">
          {i18n.language === 'zh' ? 'AAIP vs 联邦快速通道对比' : 'AAIP vs Federal Express Entry'}
        </h3>
      </div>

      {/* Comparison Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* AAIP Card */}
        <div className="bg-white rounded-lg p-5 border-2 border-green-200 relative">
          <div className="absolute -top-3 left-4 bg-green-100 px-3 py-1 rounded-full">
            <span className="text-xs font-bold text-green-700">AAIP</span>
          </div>
          <div className="mt-2">
            <div className="text-sm text-gray-600 mb-1">
              {i18n.language === 'zh' ? '平均CRS分数' : 'Avg CRS Score'}
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-2">
              {comparison.aaip?.avg_crs || 'N/A'}
            </div>
            <div className="space-y-1 text-xs text-gray-600">
              <div>
                {i18n.language === 'zh' ? '最低：' : 'Min: '}{comparison.aaip?.min_crs}
              </div>
              <div>
                {i18n.language === 'zh' ? '最高：' : 'Max: '}{comparison.aaip?.max_crs}
              </div>
              <div className="text-green-600 font-semibold mt-2">
                + 600 {i18n.language === 'zh' ? '省提名分' : 'PNP Points'}
              </div>
            </div>
          </div>
        </div>

        {/* EE PNP Card */}
        <div className="bg-white rounded-lg p-5 border-2 border-blue-200 relative">
          <div className="absolute -top-3 left-4 bg-blue-100 px-3 py-1 rounded-full">
            <span className="text-xs font-bold text-blue-700">EE PNP</span>
          </div>
          <div className="mt-2">
            <div className="text-sm text-gray-600 mb-1">
              {i18n.language === 'zh' ? '平均CRS分数' : 'Avg CRS Score'}
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-2">
              {comparison.ee_pnp?.avg_crs || 'N/A'}
            </div>
            <div className="space-y-1 text-xs text-gray-600">
              <div>
                {i18n.language === 'zh' ? '最低：' : 'Min: '}{comparison.ee_pnp?.min_crs}
              </div>
              <div>
                {i18n.language === 'zh' ? '最高：' : 'Max: '}{comparison.ee_pnp?.max_crs}
              </div>
              <div className="text-gray-500 mt-2 text-xs">
                {i18n.language === 'zh' ? '省提名持有者' : 'With Provincial Nomination'}
              </div>
            </div>
          </div>
        </div>

        {/* EE General Card */}
        <div className="bg-white rounded-lg p-5 border-2 border-indigo-200 relative">
          <div className="absolute -top-3 left-4 bg-indigo-100 px-3 py-1 rounded-full">
            <span className="text-xs font-bold text-indigo-700">EE General</span>
          </div>
          <div className="mt-2">
            <div className="text-sm text-gray-600 mb-1">
              {i18n.language === 'zh' ? '平均CRS分数' : 'Avg CRS Score'}
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-2">
              {comparison.ee_general?.avg_crs || 'N/A'}
            </div>
            <div className="space-y-1 text-xs text-gray-600">
              <div>
                {i18n.language === 'zh' ? '最低：' : 'Min: '}{comparison.ee_general?.min_crs}
              </div>
              <div>
                {i18n.language === 'zh' ? '最高：' : 'Max: '}{comparison.ee_general?.max_crs}
              </div>
              <div className="text-gray-500 mt-2 text-xs">
                {i18n.language === 'zh' ? '直接联邦抽签' : 'Direct Federal Draws'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Key Insights */}
      {insights && insights.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <TrophyIcon className="h-5 w-5 text-purple-600" />
            {i18n.language === 'zh' ? '关键对比洞察' : 'Key Comparison Insights'}
          </h4>
          
          {insights.map((insight, index) => (
            <div
              key={index}
              className="bg-white border-l-4 border-purple-400 rounded-r-lg p-4"
            >
              <div className="flex items-start gap-3">
                {insight.type === 'advantage' && <CheckCircleIcon className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />}
                {insight.type === 'info' && <InformationCircleIcon className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />}
                {insight.type === 'benefit' && <TrophyIcon className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />}
                
                <div className="flex-1">
                  <div className="font-medium text-sm text-gray-900 mb-1">
                    {insight.category}
                  </div>
                  <p className="text-sm text-gray-700">
                    {insight.message}
                  </p>
                  {insight.advantage && insight.advantage !== 'different' && (
                    <div className="mt-2">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        ✓ {i18n.language === 'zh' ? '优势：' : 'Advantage: '}{insight.advantage}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Latest Draws Preview */}
      <div className="mt-6 pt-6 border-t border-purple-200">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">
          {i18n.language === 'zh' ? '最近抽签' : 'Recent Draws'}
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* AAIP Recent */}
          <div className="bg-white rounded p-3 border border-gray-200">
            <div className="text-xs font-semibold text-green-700 mb-2">
              {i18n.language === 'zh' ? 'AAIP 最新' : 'AAIP Latest'}
            </div>
            {aaip && aaip.slice(0, 3).map((draw, idx) => (
              <div key={idx} className="text-xs text-gray-600 py-1 border-b border-gray-100 last:border-0">
                <div className="flex justify-between">
                  <span className="truncate">{draw.stream}</span>
                  <span className="font-semibold text-gray-900">CRS {draw.crs}</span>
                </div>
                <div className="text-gray-500">{draw.date}</div>
              </div>
            ))}
          </div>

          {/* EE Recent */}
          <div className="bg-white rounded p-3 border border-gray-200">
            <div className="text-xs font-semibold text-blue-700 mb-2">
              {i18n.language === 'zh' ? 'EE PNP 最新' : 'EE PNP Latest'}
            </div>
            {express_entry?.pnp && express_entry.pnp.slice(0, 3).map((draw, idx) => (
              <div key={idx} className="text-xs text-gray-600 py-1 border-b border-gray-100 last:border-0">
                <div className="flex justify-between">
                  <span>Draw #{draw.number}</span>
                  <span className="font-semibold text-gray-900">CRS {draw.crs}</span>
                </div>
                <div className="text-gray-500">{draw.date} • {draw.invitations} ITAs</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Decision Helper */}
      <div className="mt-6 bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg p-4">
        <h4 className="text-sm font-bold text-purple-900 mb-2 flex items-center gap-2">
          <InformationCircleIcon className="h-5 w-5" />
          {i18n.language === 'zh' ? '选择建议' : 'Which Path to Choose?'}
        </h4>
        <div className="text-sm text-gray-700 space-y-2">
          <div className="flex items-start gap-2">
            <span className="text-green-600 font-bold">✓</span>
            <div>
              <strong>{i18n.language === 'zh' ? '选择AAIP：' : 'Choose AAIP:'}</strong>
              <span className="ml-1">
                {i18n.language === 'zh' 
                  ? '如果您的CRS分数低于联邦抽签，但符合AAIP要求'
                  : 'If your CRS is below federal draws but meets AAIP requirements'}
              </span>
            </div>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-blue-600 font-bold">✓</span>
            <div>
              <strong>{i18n.language === 'zh' ? '选择直接EE：' : 'Choose Direct EE:'}</strong>
              <span className="ml-1">
                {i18n.language === 'zh' 
                  ? '如果您的CRS分数已经超过联邦抽签线'
                  : 'If your CRS already exceeds federal cutoffs'}
              </span>
            </div>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-purple-600 font-bold">★</span>
            <div>
              <strong>{i18n.language === 'zh' ? '双轨策略：' : 'Dual Strategy:'}</strong>
              <span className="ml-1">
                {i18n.language === 'zh' 
                  ? '同时申请AAIP和保持EE池内，提高成功率'
                  : 'Apply to AAIP while staying in EE pool for maximum chances'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExpressEntryComparison;
