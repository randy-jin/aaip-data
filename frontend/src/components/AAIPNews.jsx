import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { NewspaperIcon, CalendarIcon, ArrowTopRightOnSquareIcon } from '@heroicons/react/24/outline';
import { getAAIPNews } from '../api';
import { format, parseISO } from 'date-fns';

function AAIPNews() {
  const { t, i18n } = useTranslation();
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const articlesPerPage = 10;

  const currentLang = i18n.language;

  useEffect(() => {
    fetchNews();
  }, [currentPage]);

  const fetchNews = async () => {
    try {
      setLoading(true);
      const offset = (currentPage - 1) * articlesPerPage;
      const data = await getAAIPNews(articlesPerPage, offset);

      setNews(data.news || []);
      setTotal(data.total || 0);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to load news');
      console.error('Error fetching news:', err);
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(total / articlesPerPage);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="ml-4 text-gray-600">{t('loading.loadingData', 'Loading news...')}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">{t('error.errorLoadingData', 'Error Loading News')}</h3>
        <p className="text-red-600">{error}</p>
        <button
          onClick={fetchNews}
          className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
        >
          {t('error.retry', 'Retry')}
        </button>
      </div>
    );
  }

  if (!news || news.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
        <NewspaperIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">{t('news.noNews', 'No news articles available at this time.')}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <NewspaperIcon className="h-8 w-8 text-blue-600" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {t('news.title', 'AAIP News & Updates')}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {t('news.subtitle', 'Latest official updates from Alberta Advantage Immigration Program')}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">
              {t('news.totalArticles', 'Total Articles')}: <span className="font-semibold text-gray-900">{total}</span>
            </p>
            <p className="text-xs text-gray-400 mt-1">
              {t('news.autoTranslated', 'Auto-translated to Chinese')}
            </p>
          </div>
        </div>
      </div>

      {/* News Articles */}
      <div className="space-y-4">
        {news.map((article) => {
          const title = currentLang === 'zh' ? article.title_zh : article.title_en;
          const content = currentLang === 'zh' ? article.content_zh : article.content_en;
          const publishedDate = article.published_date ? format(parseISO(article.published_date), 'MMMM dd, yyyy') : 'Unknown date';

          return (
            <div
              key={article.id}
              className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow"
            >
              {/* Article Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <div className="flex items-center">
                      <CalendarIcon className="h-4 w-4 mr-1" />
                      {publishedDate}
                    </div>
                    <span className="text-gray-300">•</span>
                    <span className="text-xs text-gray-400">
                      {currentLang === 'zh' && (
                        <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                          {t('news.translated', 'Translated')}
                        </span>
                      )}
                      {currentLang === 'en' && (
                        <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded">
                          {t('news.original', 'Original')}
                        </span>
                      )}
                    </span>
                  </div>
                </div>
              </div>

              {/* Article Content */}
              <div className="prose max-w-none">
                <div className="text-gray-700 whitespace-pre-wrap">{content}</div>
              </div>

              {/* Footer */}
              <div className="mt-4 pt-4 border-t border-gray-100">
                <a
                  href={article.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium text-sm"
                >
                  {t('news.viewOfficial', 'View Official Source')}
                  <ArrowTopRightOnSquareIcon className="h-4 w-4 ml-1" />
                </a>
              </div>
            </div>
          );
        })}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center space-x-2 py-6">
          <button
            onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            className={`px-4 py-2 rounded ${
              currentPage === 1
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {t('pagination.previous', 'Previous')}
          </button>

          <div className="flex items-center space-x-1">
            {[...Array(totalPages)].map((_, idx) => {
              const pageNum = idx + 1;
              // Show first page, last page, current page, and pages around current
              if (
                pageNum === 1 ||
                pageNum === totalPages ||
                (pageNum >= currentPage - 1 && pageNum <= currentPage + 1)
              ) {
                return (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`px-3 py-2 rounded ${
                      currentPage === pageNum
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              } else if (pageNum === currentPage - 2 || pageNum === currentPage + 2) {
                return <span key={pageNum} className="px-2 text-gray-400">...</span>;
              }
              return null;
            })}
          </div>

          <button
            onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            className={`px-4 py-2 rounded ${
              currentPage === totalPages
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {t('pagination.next', 'Next')}
          </button>
        </div>
      )}

      {/* Disclaimer */}
      <div className="bg-amber-50 border-l-4 border-amber-500 p-4 rounded">
        <p className="text-sm text-amber-800">
          <strong>{t('news.disclaimer', 'Disclaimer')}:</strong>{' '}
          {t(
            'news.disclaimerText',
            'News articles are automatically collected and translated. For the most accurate and official information, always refer to the official Alberta government website.'
          )}
        </p>
      </div>
    </div>
  );
}

export default AAIPNews;
