import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  CalculatorIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

const WhatIfCalculator = () => {
  const { t, i18n } = useTranslation();
  const [predictions, setPredictions] = useState([]);
  const [trendData, setTrendData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Calculator inputs
  const [currentCRS, setCurrentCRS] = useState('');
  const [targetStream, setTargetStream] = useState('');
  const [results, setResults] = useState(null);

  useEffect(() => {
    fetchPredictions();
    fetchTrendData();
  }, []);

  const fetchPredictions = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/trends/prediction`
      );
      if (response.ok) {
        const data = await response.json();
        setPredictions(data.predictions || []);
      }
    } catch (err) {
      console.error('Error fetching predictions:', err);
    }
  };

  const fetchTrendData = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/trends/analysis`
      );
      if (response.ok) {
        const data = await response.json();
        setTrendData(data.data);
      }
    } catch (err) {
      console.error('Error fetching trend data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCalculate = () => {
    if (!currentCRS || !targetStream) {
      return;
    }

    const crsNum = parseInt(currentCRS);
    const streamPrediction = predictions.find(p => p.stream === targetStream);
    
    if (!streamPrediction) {
      return;
    }

    const crsData = streamPrediction.crs_prediction;
    const [minScore, maxScore] = (crsData.expected_range || '0-0').split('-').map(Number);
    
    // Calculate probability and recommendations
    let probability = 'Unknown';
    let probabilityColor = 'gray';
    let recommendation = '';
    let estimatedWaitMonths = null;
    
    if (crsNum >= maxScore) {
      probability = 'Very High (90-100%)';
      probabilityColor = 'green';
      recommendation = i18n.language === 'zh' 
        ? '您的分数超过最近的最高分！您很可能在下次抽签中获邀。'
        : 'Your score exceeds recent maximum! You\'re likely to be invited in the next draw.';
      estimatedWaitMonths = '<1';
    } else if (crsNum >= crsData.recent_avg) {
      probability = 'High (70-90%)';
      probabilityColor = 'green';
      recommendation = i18n.language === 'zh'
        ? '您的分数高于最近平均分，有很高的机会在接下来的几次抽签中获邀。'
        : 'Your score is above recent average. High chance in upcoming draws.';
      estimatedWaitMonths = '1-2';
    } else if (crsNum >= minScore) {
      probability = 'Moderate (50-70%)';
      probabilityColor = 'yellow';
      recommendation = i18n.language === 'zh'
        ? '您的分数在最近的范围内。可能需要等待几次抽签。'
        : 'Your score is within recent range. May need to wait for a few draws.';
      estimatedWaitMonths = '2-4';
    } else {
      probability = 'Low (<50%)';
      probabilityColor = 'red';
      const pointsNeeded = minScore - crsNum;
      recommendation = i18n.language === 'zh'
        ? `您的分数低于最近的最低分${pointsNeeded}分。建议提升您的CRS分数。`
        : `Your score is ${pointsNeeded} points below recent minimum. Consider improving your CRS score.`;
      estimatedWaitMonths = '4+';
    }

    // Generate improvement suggestions
    const improvements = generateImprovementSuggestions(crsNum, maxScore, i18n.language);

    setResults({
      probability,
      probabilityColor,
      recommendation,
      estimatedWaitMonths,
      nextDrawDate: streamPrediction.predicted_next_draw,
      scoreGap: Math.max(0, minScore - crsNum),
      improvements,
      trend: crsData.trend
    });
  };

  const generateImprovementSuggestions = (current, target, lang) => {
    const gap = target - current;
    
    if (gap <= 0) {
      return [];
    }

    const suggestions = [];

    if (gap >= 50) {
      suggestions.push({
        action: lang === 'zh' ? '提升语言成绩（IELTS/TEF）' : 'Improve language scores (IELTS/TEF)',
        potential: '+30-50',
        effort: lang === 'zh' ? '中等' : 'Moderate'
      });
    }

    if (gap >= 30) {
      suggestions.push({
        action: lang === 'zh' ? '获得加拿大工作经验' : 'Gain Canadian work experience',
        potential: '+40-70',
        effort: lang === 'zh' ? '高（需时间）' : 'High (time required)'
      });
    }

    if (gap >= 20) {
      suggestions.push({
        action: lang === 'zh' ? '配偶提升语言/学历' : 'Spouse improve language/education',
        potential: '+10-20',
        effort: lang === 'zh' ? '中等' : 'Moderate'
      });
    }

    if (gap >= 15) {
      suggestions.push({
        action: lang === 'zh' ? '完成额外学历认证（ECA）' : 'Complete additional education credential (ECA)',
        potential: '+15-30',
        effort: lang === 'zh' ? '低' : 'Low'
      });
    }

    return suggestions;
  };

  const getStreamOptions = () => {
    return predictions.map(p => ({
      value: p.stream,
      label: p.stream
    }));
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow-md p-6 border border-blue-100">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <CalculatorIcon className="h-7 w-7 text-blue-600" />
        <div>
          <h3 className="text-xl font-bold text-gray-900">
            {i18n.language === 'zh' ? '可能性计算器' : '"What If" Calculator'}
          </h3>
          <p className="text-sm text-gray-600">
            {i18n.language === 'zh' 
              ? '根据历史数据估算您的获邀概率'
              : 'Estimate your invitation probability based on historical data'}
          </p>
        </div>
      </div>

      {/* Warning Banner */}
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
        <div className="flex items-start gap-3">
          <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="font-semibold text-yellow-900 mb-1">
              {i18n.language === 'zh' ? '重要声明' : 'Important Disclaimer'}
            </p>
            <p className="text-yellow-800">
              {i18n.language === 'zh'
                ? '这些预测基于历史数据的统计分析，仅供参考。移民政策可能随时变化，实际结果可能有所不同。'
                : 'These predictions are statistical estimates based on historical patterns. Immigration policies can change, and actual results may vary.'}
            </p>
          </div>
        </div>
      </div>

      {/* Calculator Input */}
      <div className="bg-white rounded-lg p-6 mb-6 border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {i18n.language === 'zh' ? '您的CRS分数' : 'Your CRS Score'}
            </label>
            <input
              type="number"
              value={currentCRS}
              onChange={(e) => setCurrentCRS(e.target.value)}
              placeholder={i18n.language === 'zh' ? '输入分数 (0-1200)' : 'Enter score (0-1200)'}
              min="0"
              max="1200"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {i18n.language === 'zh' ? '目标类别' : 'Target Stream'}
            </label>
            <select
              value={targetStream}
              onChange={(e) => setTargetStream(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">
                {i18n.language === 'zh' ? '选择类别' : 'Select stream'}
              </option>
              {getStreamOptions().map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={handleCalculate}
          disabled={!currentCRS || !targetStream}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
        >
          {i18n.language === 'zh' ? '计算概率' : 'Calculate Probability'}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-4">
          {/* Probability Result */}
          <div className="bg-white rounded-lg p-6 border-2 border-blue-200">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-bold text-gray-900">
                {i18n.language === 'zh' ? '获邀概率' : 'Invitation Probability'}
              </h4>
              <span className={`px-4 py-2 rounded-full text-sm font-bold ${
                results.probabilityColor === 'green' ? 'bg-green-100 text-green-800' :
                results.probabilityColor === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {results.probability}
              </span>
            </div>

            <p className="text-gray-700 mb-4">{results.recommendation}</p>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <ClockIcon className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="text-gray-600">
                    {i18n.language === 'zh' ? '预计等待' : 'Est. Wait'}
                  </div>
                  <div className="font-semibold text-gray-900">
                    {results.estimatedWaitMonths} {i18n.language === 'zh' ? '个月' : 'months'}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <ChartBarIcon className="h-5 w-5 text-blue-600" />
                <div>
                  <div className="text-gray-600">
                    {i18n.language === 'zh' ? '分差' : 'Score Gap'}
                  </div>
                  <div className="font-semibold text-gray-900">
                    {results.scoreGap} {i18n.language === 'zh' ? '分' : 'points'}
                  </div>
                </div>
              </div>
            </div>

            {results.nextDrawDate && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center gap-2 text-sm">
                  <InformationCircleIcon className="h-5 w-5 text-blue-600" />
                  <span className="text-gray-600">
                    {i18n.language === 'zh' ? '预计下次抽签：' : 'Next draw estimate: '}
                    <span className="font-semibold text-gray-900">
                      {new Date(results.nextDrawDate).toLocaleDateString()}
                    </span>
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Improvement Suggestions */}
          {results.improvements && results.improvements.length > 0 && (
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <h4 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <ArrowTrendingUpIcon className="h-6 w-6 text-green-600" />
                {i18n.language === 'zh' ? '提分建议' : 'Score Improvement Suggestions'}
              </h4>

              <div className="space-y-3">
                {results.improvements.map((suggestion, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                    <CheckCircleIcon className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{suggestion.action}</div>
                      <div className="text-sm text-gray-600 mt-1">
                        <span className="text-green-700 font-semibold">{suggestion.potential}</span>
                        {' '}{i18n.language === 'zh' ? '分 • 难度：' : ' points • Effort: '}
                        {suggestion.effort}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Stream Predictions Summary */}
      {!results && predictions.length > 0 && (
        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <h4 className="text-sm font-semibold text-gray-700 mb-4">
            {i18n.language === 'zh' ? '最近各类别趋势' : 'Recent Stream Trends'}
          </h4>
          
          <div className="space-y-3">
            {predictions.slice(0, 4).map((pred, index) => (
              <div key={index} className="flex items-center justify-between text-sm py-2 border-b border-gray-100 last:border-0">
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{pred.stream}</div>
                  <div className="text-xs text-gray-600">
                    {i18n.language === 'zh' ? 'CRS范围：' : 'CRS Range: '}
                    {pred.crs_prediction.expected_range || 'N/A'}
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-xs font-semibold ${
                    pred.crs_prediction.trend === 'decreasing' ? 'text-green-600' :
                    pred.crs_prediction.trend === 'increasing' ? 'text-red-600' :
                    'text-gray-600'
                  }`}>
                    {pred.crs_prediction.trend === 'decreasing' ? '📉 ' : 
                     pred.crs_prediction.trend === 'increasing' ? '📈 ' : '➡️ '}
                    {pred.crs_prediction.trend}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default WhatIfCalculator;
