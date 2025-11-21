import { useTranslation } from 'react-i18next';
import { ExclamationTriangleIcon, InformationCircleIcon } from '@heroicons/react/24/outline';

function DisclaimerBanner() {
  const { t } = useTranslation();

  return (
    <div className="bg-gradient-to-r from-amber-50 via-yellow-50 to-amber-50 border-l-4 border-amber-500 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <ExclamationTriangleIcon className="h-6 w-6 text-amber-600 mt-0.5" aria-hidden="true" />
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-1">
              <h2 className="text-lg font-bold text-amber-900">
                {t('disclaimer.title', 'IMPORTANT DISCLAIMER')}
              </h2>
              <InformationCircleIcon className="h-5 w-5 text-amber-700" />
            </div>
            <p className="text-base font-semibold text-amber-800 leading-relaxed">
              {t(
                'disclaimer.main',
                'This site is an UNOFFICIAL data analysis tool, provided for historical trend reference only, and does NOT represent the government\'s position or official information.'
              )}
            </p>
            <div className="mt-3 space-y-1.5 text-sm text-amber-700">
              <p className="flex items-start">
                <span className="mr-2">•</span>
                <span>
                  {t(
                    'disclaimer.dataSource',
                    'All data is collected from publicly available sources and may not reflect real-time updates.'
                  )}
                </span>
              </p>
              <p className="flex items-start">
                <span className="mr-2">•</span>
                <span>
                  {t(
                    'disclaimer.predictions',
                    'Predictions and insights are based on statistical analysis and should not be used as the sole basis for immigration decisions.'
                  )}
                </span>
              </p>
              <p className="flex items-start">
                <span className="mr-2">•</span>
                <span>
                  {t(
                    'disclaimer.officialSource',
                    'Always refer to official Alberta government immigration website for authoritative information:'
                  )}{' '}
                  <a
                    href="https://www.alberta.ca/aaip"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-semibold text-amber-900 underline hover:text-amber-950"
                  >
                    www.alberta.ca/aaip
                  </a>
                </span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DisclaimerBanner;
