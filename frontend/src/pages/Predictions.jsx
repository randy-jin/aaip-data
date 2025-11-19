import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import WhatIfCalculator from '../components/WhatIfCalculator';
import {
  SparklesIcon,
  ClockIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CalendarIcon
} from '@heroicons/react/24/outline';

const Predictions = () => {
  const { t, i18n } = useTranslation();
  const [predictions, setPredictions] = useState([]);
  const [trendData, setTrendData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [predResp, trendResp] = await Promise.all([
        fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/trends/prediction`),
        fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/trends/analysis`)
      ]);

      if (predResp.ok) {
        const data = await predResp.json();
        setPredictions(data.predictions || []);
      }

      if (trendResp.ok) {
        const data = await trendResp.json();
        setTrendData(data.data);
      }
    } catch (err) {
      console.error('Error fetching prediction data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend) => {
    if (trend === 'increasing') return '📈';
    if (trend === 'decreasing') return '📉';
    return '➡️';
  };

  const getTrendColor = (trend) => {
    if (trend === 'decreasing') return 'text-green-600';
    if (trend === 'increasing') return 'text-red-600';
    return 'text-gray-600';
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Page Header */}
      <div>
        <div className="flex items-center gap-3 mb-3">
          <SparklesIcon className="h-8 w-8 text-purple-600" />
          <h1 className="text-3xl font-bold text-gray-900">
            {i18n.language === 'zh' ? '趋势预测与分析' : 'Trends & Predictions'}
          </h1>
        </div>
        <p className="text-gray-600">
          {i18n.language === 'zh'
            ? '基于历史数据的统计分析和预测工具'
            : 'Statistical analysis and prediction tools based on historical data'}
        </p>
      </div>

      {/* Important Notice */}
      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border-l-4 border-yellow-400 rounded-r-lg p-6 shadow-sm">
        <div className="flex items-start gap-4">
          <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-bold text-gray-900 mb-2">
              {i18n.language === 'zh' ? '⚠️ 重要提示' : '⚠️ Important Notice'}
            </h3>
            <p className="text-sm text-gray-700 leading-relaxed">
              {i18n.language === 'zh'
                ? '以下所有预测和分析都基于历史数据的统计模式，仅供参考。加拿大移民政策可能因经济、政治等因素随时调整，实际抽签时间、分数和邀请数量可能与预测不同。请以官方信息为准，不要将预测作为唯一决策依据。'
                : 'All predictions and analyses below are based on statistical patterns from historical data and are for reference only. Canadian immigration policies can change due to economic, political, and other factors. Actual draw dates, scores, and invitation numbers may differ from predictions. Always rely on official information and do not use predictions as your sole decision-making basis.'}
            </p>
          </div>
        </div>
      </div>

      {/* What If Calculator */}
      <WhatIfCalculator />

      {/* Next Draw Predictions */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-3 mb-6">
          <CalendarIcon className="h-6 w-6 text-indigo-600" />
          <h2 className="text-xl font-bold text-gray-900">
            {i18n.language === 'zh' ? '下次抽签预测' : 'Next Draw Predictions'}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {predictions.map((pred, index) => (
            <div
              key={index}
              className="border border-gray-200 rounded-lg p-4 hover:border-indigo-300 hover:shadow-md transition-all"
            >
              <div className="font-semibold text-gray-900 mb-3 text-sm">
                {pred.stream}
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">
                    {i18n.language === 'zh' ? '上次抽签' : 'Last Draw'}
                  </span>
                  <span className="font-medium text-gray-900">
                    {new Date(pred.last_draw_date).toLocaleDateString()}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm bg-indigo-50 p-2 rounded">
                  <span className="text-gray-700 font-medium">
                    {i18n.language === 'zh' ? '预计下次' : 'Next Est.'}
                  </span>
                  <span className="font-semibold text-indigo-700">
                    {new Date(pred.predicted_next_draw).toLocaleDateString()}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">
                    {i18n.language === 'zh' ? 'CRS范围' : 'CRS Range'}
                  </span>
                  <span className="font-medium text-gray-900">
                    {pred.crs_prediction.expected_range || 'N/A'}
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs pt-2 border-t border-gray-200">
                  <span className="text-gray-500">
                    {i18n.language === 'zh' ? '趋势' : 'Trend'}
                  </span>
                  <span className={`font-semibold ${getTrendColor(pred.crs_prediction.trend)}`}>
                    {getTrendIcon(pred.crs_prediction.trend)} {pred.crs_prediction.trend}
                  </span>
                </div>

                <div className="text-xs text-gray-500 pt-2 border-t border-gray-100">
                  {i18n.language === 'zh' ? '可信度：' : 'Confidence: '}
                  <span className="font-medium">{pred.confidence}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 text-xs text-gray-500 text-center">
          {i18n.language === 'zh'
            ? '* 预测基于历史平均间隔，实际时间可能有所不同'
            : '* Predictions based on historical average intervals, actual timing may vary'}
        </div>
      </div>

      {/* Historical Trends Summary */}
      {trendData && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center gap-3 mb-6">
            <ChartBarIcon className="h-6 w-6 text-green-600" />
            <h2 className="text-xl font-bold text-gray-900">
              {i18n.language === 'zh' ? '历史趋势总结' : 'Historical Trends Summary'}
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Total Draws */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
              <div className="text-sm text-blue-700 font-medium mb-1">
                {i18n.language === 'zh' ? '总抽签次数' : 'Total Draws'}
              </div>
              <div className="text-3xl font-bold text-blue-900">
                {trendData.metadata?.total_draws || 0}
              </div>
            </div>

            {/* Most Active Quarter */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
              <div className="text-sm text-green-700 font-medium mb-1">
                {i18n.language === 'zh' ? '最活跃季度' : 'Most Active Quarter'}
              </div>
              <div className="text-3xl font-bold text-green-900">
                {trendData.seasonal_patterns?.most_active_quarter?.quarter || 'N/A'}
              </div>
              <div className="text-xs text-green-700 mt-1">
                {trendData.seasonal_patterns?.most_active_quarter?.count} {i18n.language === 'zh' ? '次抽签' : 'draws'}
              </div>
            </div>

            {/* Data Range */}
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
              <div className="text-sm text-purple-700 font-medium mb-1">
                {i18n.language === 'zh' ? '数据起始' : 'Data Since'}
              </div>
              <div className="text-lg font-bold text-purple-900">
                {trendData.metadata?.date_range?.earliest 
                  ? new Date(trendData.metadata.date_range.earliest).toLocaleDateString()
                  : 'N/A'}
              </div>
            </div>

            {/* Last Updated */}
            <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4">
              <div className="text-sm text-orange-700 font-medium mb-1">
                {i18n.language === 'zh' ? '最近更新' : 'Last Updated'}
              </div>
              <div className="text-lg font-bold text-orange-900">
                {trendData.metadata?.date_range?.latest 
                  ? new Date(trendData.metadata.date_range.latest).toLocaleDateString()
                  : 'N/A'}
              </div>
            </div>
          </div>

          {/* CRS Trends by Stream */}
          {trendData.crs_trends && Object.keys(trendData.crs_trends).length > 0 && (
            <div className="mt-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">
                {i18n.language === 'zh' ? 'CRS分数趋势（按类别）' : 'CRS Score Trends by Stream'}
              </h3>
              
              <div className="space-y-3">
                {Object.entries(trendData.crs_trends).map(([stream, data]) => (
                  <div key={stream} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900 text-sm">{stream}</span>
                      <span className={`text-sm font-semibold ${getTrendColor(data.trend)}`}>
                        {getTrendIcon(data.trend)} {data.trend}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-2 text-xs">
                      <div>
                        <span className="text-gray-600">{i18n.language === 'zh' ? '最近均分' : 'Recent Avg'}</span>
                        <div className="font-semibold text-gray-900">{data.recent_avg}</div>
                      </div>
                      <div>
                        <span className="text-gray-600">{i18n.language === 'zh' ? '范围' : 'Range'}</span>
                        <div className="font-semibold text-gray-900">
                          {data.recent_min}-{data.recent_max}
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-600">{i18n.language === 'zh' ? '历史最低' : 'All-Time Low'}</span>
                        <div className="font-semibold text-green-700">{data.all_time_min}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Methodology Note */}
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <h3 className="font-bold text-gray-900 mb-3">
          {i18n.language === 'zh' ? '📊 分析方法说明' : '📊 Methodology'}
        </h3>
        <div className="text-sm text-gray-700 space-y-2 leading-relaxed">
          <p>
            {i18n.language === 'zh'
              ? '• 下次抽签日期预测：基于每个类别的历史平均抽签间隔'
              : '• Next draw date predictions: Based on historical average draw intervals per stream'}
          </p>
          <p>
            {i18n.language === 'zh'
              ? '• CRS分数范围：基于最近5次抽签的分数范围'
              : '• CRS score ranges: Based on the most recent 5 draws'}
          </p>
          <p>
            {i18n.language === 'zh'
              ? '• 趋势判断：对比最近5次与之前5次的平均分数'
              : '• Trend determination: Comparing recent 5 draws vs previous 5 draws average'}
          </p>
          <p>
            {i18n.language === 'zh'
              ? '• 概率估算：基于您的分数与历史分数分布的相对位置'
              : '• Probability estimates: Based on your score relative to historical score distribution'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Predictions;
