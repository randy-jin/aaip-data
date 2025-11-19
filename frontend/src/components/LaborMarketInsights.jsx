import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  BriefcaseIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  MinusIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import AlbertaEconomyIndicators from './AlbertaEconomyIndicators';
import ExpressEntryComparison from './ExpressEntryComparison';

const LaborMarketInsights = () => {
  const { t, i18n } = useTranslation();

  // Manually curated labor market context (update quarterly)
  const laborMarketData = {
    lastUpdated: '2025-Q4',
    updateDate: 'November 2025',
    
    streams: [
      {
        name: 'Healthcare (DHCP)',
        nameZh: '医疗保健途径',
        demand: 'strong',
        trend: 'up',
        summary: 'Alberta continues to face healthcare worker shortages. Strong demand for nurses, healthcare aides, and allied health professionals.',
        summaryZh: '阿尔伯塔省持续面临医疗工作者短缺。对护士、医疗助理和相关健康专业人员有强劲需求。',
        recommendation: 'Excellent time for healthcare workers to apply. DHCP remains highly active.',
        recommendationZh: '医疗保健工作者申请的绝佳时机。DHCP保持高度活跃。',
        sectors: ['Registered Nurses', 'Licensed Practical Nurse', 'Healthcare Aides', 'Medical Lab Technologists'],
        sectorsZh: ['注册护士', '执业护士', '医疗助理', '医学实验室技术人员']
      },
      {
        name: 'Tourism & Hospitality',
        nameZh: '旅游与酒店业',
        demand: 'moderate',
        trend: 'stable',
        summary: 'Hospitality sector recovering post-pandemic. Seasonal demand for cooks, food service workers, and hotel staff.',
        summaryZh: '酒店业疫情后恢复中。对厨师、餐饮服务人员和酒店员工有季节性需求。',
        recommendation: 'Good opportunities exist, especially in Calgary and Banff area. Competition is moderate.',
        recommendationZh: '有良好机会，特别是在卡尔加里和班夫地区。竞争适中。',
        sectors: ['Cooks', 'Food Service Supervisors', 'Hotel Front Desk', 'Restaurant Managers'],
        sectorsZh: ['厨师', '餐饮服务主管', '酒店前台', '餐厅经理']
      },
      {
        name: 'Technology (Accelerated Tech)',
        nameZh: '科技加速通道',
        demand: 'moderate',
        trend: 'down',
        summary: 'Tech sector consolidating after recent growth. Selective hiring focused on experienced professionals.',
        summaryZh: '科技行业在近期增长后进行整合。有选择地聘用有经验的专业人士。',
        recommendation: 'Competitive. Strong credentials and work experience recommended. AI/ML skills are valued.',
        recommendationZh: '竞争激烈。建议有强大资历和工作经验。AI/ML技能受重视。',
        sectors: ['Software Engineers', 'Data Scientists', 'DevOps Engineers', 'Cybersecurity'],
        sectorsZh: ['软件工程师', '数据科学家', 'DevOps工程师', '网络安全']
      },
      {
        name: 'Construction & Trades',
        nameZh: '建筑与技工',
        demand: 'strong',
        trend: 'up',
        summary: 'Infrastructure projects and housing development driving demand for skilled trades. Electricians, plumbers, and carpenters in high demand.',
        summaryZh: '基础设施项目和住房开发推动对技术工人的需求。电工、水管工和木工需求旺盛。',
        recommendation: 'Strong opportunities through Alberta Opportunity Stream for certified tradespeople.',
        recommendationZh: '持证技工通过阿尔伯塔机会类别有强劲机会。',
        sectors: ['Electricians', 'Plumbers', 'Carpenters', 'Welders'],
        sectorsZh: ['电工', '水管工', '木工', '焊工']
      },
      {
        name: 'Agriculture & Rural',
        nameZh: '农业与乡村',
        demand: 'moderate',
        trend: 'stable',
        summary: 'Steady demand in rural areas. Farm workers, meat processing, and agricultural managers needed.',
        summaryZh: '农村地区需求稳定。需要农场工人、肉类加工和农业管理人员。',
        recommendation: 'Consider Rural Renewal Stream if working outside major cities. Lower competition.',
        recommendationZh: '如在主要城市外工作，可考虑农村振兴类别。竞争较低。',
        sectors: ['Farm Supervisors', 'Agricultural Workers', 'Meat Cutters', 'Food Processing'],
        sectorsZh: ['农场主管', '农业工人', '切肉工', '食品加工']
      },
      {
        name: 'General Business & Services',
        nameZh: '一般商业与服务',
        demand: 'moderate',
        trend: 'stable',
        summary: 'Diverse opportunities in retail, transportation, and services. Broad eligibility through AOS.',
        summaryZh: '零售、运输和服务领域机会多样。通过AOS资格广泛。',
        recommendation: 'Accessible for many occupations. Focus on gaining Alberta work experience.',
        recommendationZh: '许多职业都可申请。重点是获得阿尔伯塔工作经验。',
        sectors: ['Retail Supervisors', 'Truck Drivers', 'Administrative Assistants', 'Customer Service'],
        sectorsZh: ['零售主管', '卡车司机', '行政助理', '客户服务']
      }
    ],
    
    generalContext: {
      title: 'Alberta Economic Outlook',
      titleZh: '阿尔伯塔省经济展望',
      summary: "Alberta's economy remains robust with continued investment in energy, technology, and infrastructure. Population growth is driving demand across multiple sectors. The provincial government is actively working to address labor shortages through immigration programs.",
      summaryZh: '阿尔伯塔省经济保持强劲，能源、技术和基础设施领域持续投资。人口增长推动多个行业需求。省政府正积极通过移民项目解决劳动力短缺问题。'
    }
  };

  const getDemandBadge = (demand) => {
    const badges = {
      strong: {
        color: 'bg-green-100 text-green-800 border-green-300',
        icon: <CheckCircleIcon className="h-4 w-4" />,
        text: 'Strong Demand',
        textZh: '需求旺盛'
      },
      moderate: {
        color: 'bg-blue-100 text-blue-800 border-blue-300',
        icon: <InformationCircleIcon className="h-4 w-4" />,
        text: 'Moderate Demand',
        textZh: '需求适中'
      },
      declining: {
        color: 'bg-amber-100 text-amber-800 border-amber-300',
        icon: <ExclamationTriangleIcon className="h-4 w-4" />,
        text: 'Competitive',
        textZh: '竞争激烈'
      }
    };
    return badges[demand] || badges.moderate;
  };

  const getTrendIcon = (trend) => {
    if (trend === 'up') return <ArrowTrendingUpIcon className="h-5 w-5 text-green-600" />;
    if (trend === 'down') return <ArrowTrendingDownIcon className="h-5 w-5 text-red-600" />;
    return <MinusIcon className="h-5 w-5 text-gray-600" />;
  };

  return (
    <div className="space-y-6">
      {/* Alberta Economic Indicators */}
      <AlbertaEconomyIndicators />

      {/* Express Entry Comparison */}
      <ExpressEntryComparison />

      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-3 mb-4">
          <BriefcaseIcon className="h-8 w-8 text-indigo-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {t('laborMarket.title', 'Alberta Labor Market Context')}
            </h2>
            <p className="text-sm text-gray-600">
              {t('laborMarket.lastUpdated', 'Last Updated')}: {laborMarketData.updateDate}
            </p>
          </div>
        </div>

        {/* General Context */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-2">
            {i18n.language === 'zh' ? laborMarketData.generalContext.titleZh : laborMarketData.generalContext.title}
          </h3>
          <p className="text-gray-700 text-sm">
            {i18n.language === 'zh' ? laborMarketData.generalContext.summaryZh : laborMarketData.generalContext.summary}
          </p>
        </div>
      </div>

      {/* Stream-by-Stream Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {laborMarketData.streams.map((stream, index) => {
          const badge = getDemandBadge(stream.demand);
          return (
            <div key={index} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
              <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900 mb-2">
                      {i18n.language === 'zh' ? stream.nameZh : stream.name}
                    </h3>
                    <div className="flex items-center gap-2">
                      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium border ${badge.color}`}>
                        {badge.icon}
                        {i18n.language === 'zh' ? badge.textZh : badge.text}
                      </span>
                      {getTrendIcon(stream.trend)}
                    </div>
                  </div>
                </div>

                {/* Summary */}
                <p className="text-gray-700 text-sm mb-4">
                  {i18n.language === 'zh' ? stream.summaryZh : stream.summary}
                </p>

                {/* Key Sectors */}
                <div className="mb-4">
                  <p className="text-xs font-semibold text-gray-600 mb-2">
                    {t('laborMarket.keySectors', 'Key Occupations')}:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {(i18n.language === 'zh' ? stream.sectorsZh : stream.sectors).map((sector, idx) => (
                      <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                        {sector}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Recommendation */}
                <div className="bg-indigo-50 border-l-4 border-indigo-400 p-3 rounded">
                  <p className="text-sm font-medium text-gray-800">
                    💡 {i18n.language === 'zh' ? stream.recommendationZh : stream.recommendation}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Important Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
          <InformationCircleIcon className="h-5 w-5 text-amber-600" />
          {t('laborMarket.important', 'Important Information')}
        </h3>
        <p className="text-gray-700 text-sm mb-2">
          {t('laborMarket.contextNote', 'This labor market information provides general context about employment trends in Alberta. It does NOT guarantee AAIP nomination outcomes.')}
        </p>
        <p className="text-gray-700 text-sm">
          {t('laborMarket.updateSchedule', 'This page is manually updated quarterly based on Alberta economic reports and government publications. For the most accurate AAIP information, refer to the official')} <a href="https://www.alberta.ca/aaip" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline font-medium">Alberta.ca AAIP page</a>.
        </p>
      </div>
    </div>
  );
};

export default LaborMarketInsights;
