import React, { useState, useEffect } from 'react';
import {
  UserGroupIcon,
  ChatBubbleLeftRightIcon,
  HeartIcon,
  PlusIcon,
  FunnelIcon,
  CheckCircleIcon,
  ClockIcon,
  TrophyIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';

const API_BASE = 'http://localhost:8000';

const SuccessStories = () => {
  const [stories, setStories] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showSubmitForm, setShowSubmitForm] = useState(false);
  const [filters, setFilters] = useState({ stream: '', story_type: '' });
  
  // Form state
  const [formData, setFormData] = useState({
    story_type: 'nomination',
    aaip_stream: 'Express Entry',
    timeline_submitted: '',
    timeline_nominated: '',
    timeline_pr_approved: '',
    noc_code: '',
    crs_score: '',
    work_permit_type: '',
    city: '',
    story_text: '',
    tips: '',
    challenges: '',
    author_name: 'Anonymous',
    is_anonymous: true,
    email: ''
  });

  useEffect(() => {
    fetchStories();
    fetchStats();
  }, [filters]);

  const fetchStories = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.stream) params.append('stream', filters.stream);
      if (filters.story_type) params.append('story_type', filters.story_type);
      
      const response = await fetch(`${API_BASE}/api/success-stories?${params}`);
      const data = await response.json();
      setStories(data.stories || []);
    } catch (error) {
      console.error('Error fetching stories:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/success-stories/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.story_text.length < 50) {
      alert('Please provide a story with at least 50 characters');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/success-stories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        alert('Thank you for sharing your story! It will help others in the community.');
        setShowSubmitForm(false);
        setFormData({
          story_type: 'nomination',
          aaip_stream: 'Express Entry',
          timeline_submitted: '',
          timeline_nominated: '',
          timeline_pr_approved: '',
          noc_code: '',
          crs_score: '',
          work_permit_type: '',
          city: '',
          story_text: '',
          tips: '',
          challenges: '',
          author_name: 'Anonymous',
          is_anonymous: true,
          email: ''
        });
        fetchStories();
        fetchStats();
      } else {
        alert('Failed to submit story. Please try again.');
      }
    } catch (error) {
      console.error('Error submitting story:', error);
      alert('Failed to submit story. Please try again.');
    }
  };

  const handleMarkHelpful = async (storyId) => {
    try {
      const response = await fetch(`${API_BASE}/api/success-stories/${storyId}/helpful`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        setStories(stories.map(story => 
          story.id === storyId 
            ? { ...story, helpful_count: data.helpful_count }
            : story
        ));
      }
    } catch (error) {
      console.error('Error marking as helpful:', error);
    }
  };

  const calculateDuration = (startDate, endDate) => {
    if (!startDate || !endDate) return null;
    const start = new Date(startDate);
    const end = new Date(endDate);
    const days = Math.floor((end - start) / (1000 * 60 * 60 * 24));
    return days;
  };

  const STORY_TYPES = [
    { value: 'nomination', label: 'AAIP Nomination', icon: TrophyIcon },
    { value: 'pr_approval', label: 'PR Approval', icon: CheckCircleIcon },
    { value: 'job_offer', label: 'Job Offer', icon: ClockIcon },
    { value: 'settlement', label: 'Settlement Experience', icon: UserGroupIcon }
  ];

  const STREAMS = [
    'Express Entry',
    'AOS',
    'Rural Renewal',
    'Farm',
    'Graduate Entrepreneur',
    'Foreign Graduate Entrepreneur',
    'Rural Entrepreneur',
    'Tourism and Hospitality',
    'Dedicated Healthcare',
    'Accelerated Tech'
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <UserGroupIcon className="h-8 w-8" />
              <h2 className="text-2xl font-bold">Community Success Stories</h2>
            </div>
            <p className="text-green-50">
              Real experiences from AAIP applicants who made it! Learn from their journey.
            </p>
          </div>
          <button
            onClick={() => setShowSubmitForm(!showSubmitForm)}
            className="bg-white text-green-600 px-6 py-3 rounded-lg font-semibold hover:bg-green-50 transition flex items-center space-x-2"
          >
            <PlusIcon className="h-5 w-5" />
            <span>Share Your Story</span>
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-4 shadow">
            <div className="text-3xl font-bold text-green-600">{stats.overall?.total_stories || 0}</div>
            <div className="text-sm text-gray-600">Success Stories</div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow">
            <div className="text-3xl font-bold text-blue-600">{stats.overall?.streams_covered || 0}</div>
            <div className="text-sm text-gray-600">Streams Covered</div>
          </div>
          {stats.overall?.avg_days_to_nomination && (
            <div className="bg-white rounded-lg p-4 shadow">
              <div className="text-3xl font-bold text-purple-600">
                {Math.round(stats.overall.avg_days_to_nomination)}
              </div>
              <div className="text-sm text-gray-600">Avg Days to Nomination</div>
            </div>
          )}
          {stats.overall?.avg_days_to_pr && (
            <div className="bg-white rounded-lg p-4 shadow">
              <div className="text-3xl font-bold text-orange-600">
                {Math.round(stats.overall.avg_days_to_pr)}
              </div>
              <div className="text-sm text-gray-600">Avg Days to PR (from nomination)</div>
            </div>
          )}
        </div>
      )}

      {/* Submit Form Modal */}
      {showSubmitForm && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-bold mb-4">Share Your Success Story</h3>
          <p className="text-sm text-gray-600 mb-6">
            Help others by sharing your AAIP journey. Your story can inspire and guide future applicants!
          </p>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Story Type *</label>
                <select
                  value={formData.story_type}
                  onChange={(e) => setFormData({...formData, story_type: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                  required
                >
                  {STORY_TYPES.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">AAIP Stream *</label>
                <select
                  value={formData.aaip_stream}
                  onChange={(e) => setFormData({...formData, aaip_stream: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                  required
                >
                  {STREAMS.map(stream => (
                    <option key={stream} value={stream}>{stream}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Date Submitted</label>
                <input
                  type="date"
                  value={formData.timeline_submitted}
                  onChange={(e) => setFormData({...formData, timeline_submitted: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Date Nominated</label>
                <input
                  type="date"
                  value={formData.timeline_nominated}
                  onChange={(e) => setFormData({...formData, timeline_nominated: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">NOC Code</label>
                <input
                  type="text"
                  value={formData.noc_code}
                  onChange={(e) => setFormData({...formData, noc_code: e.target.value})}
                  placeholder="e.g., 21232"
                  className="w-full border rounded px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">CRS Score</label>
                <input
                  type="number"
                  value={formData.crs_score}
                  onChange={(e) => setFormData({...formData, crs_score: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Work Permit Type</label>
                <select
                  value={formData.work_permit_type}
                  onChange={(e) => setFormData({...formData, work_permit_type: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="">Select...</option>
                  <option value="LIMA">LIMA</option>
                  <option value="LMIA-exempt">LMIA-exempt</option>
                  <option value="Open Work Permit">Open Work Permit</option>
                  <option value="BOWP">BOWP</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">City in Alberta</label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData({...formData, city: e.target.value})}
                  placeholder="e.g., Calgary"
                  className="w-full border rounded px-3 py-2"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Your Story * (min 50 characters)</label>
              <textarea
                value={formData.story_text}
                onChange={(e) => setFormData({...formData, story_text: e.target.value})}
                rows={6}
                className="w-full border rounded px-3 py-2"
                placeholder="Share your AAIP journey, what worked, challenges you faced, etc."
                required
              />
              <div className="text-xs text-gray-500 mt-1">
                {formData.story_text.length} / 50 minimum
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Tips for Others (Optional)</label>
              <textarea
                value={formData.tips}
                onChange={(e) => setFormData({...formData, tips: e.target.value})}
                rows={3}
                className="w-full border rounded px-3 py-2"
                placeholder="What advice would you give to future applicants?"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Challenges You Faced (Optional)</label>
              <textarea
                value={formData.challenges}
                onChange={(e) => setFormData({...formData, challenges: e.target.value})}
                rows={3}
                className="w-full border rounded px-3 py-2"
                placeholder="What difficulties did you encounter and how did you overcome them?"
              />
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.is_anonymous}
                onChange={(e) => setFormData({...formData, is_anonymous: e.target.checked})}
                className="rounded"
              />
              <label className="text-sm">Post anonymously (recommended)</label>
            </div>

            {!formData.is_anonymous && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Your Name</label>
                  <input
                    type="text"
                    value={formData.author_name}
                    onChange={(e) => setFormData({...formData, author_name: e.target.value})}
                    className="w-full border rounded px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Email (optional)</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full border rounded px-3 py-2"
                  />
                </div>
              </div>
            )}

            <div className="flex space-x-3">
              <button
                type="submit"
                className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition"
              >
                Submit Story
              </button>
              <button
                type="button"
                onClick={() => setShowSubmitForm(false)}
                className="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300 transition"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg p-4 shadow">
        <div className="flex items-center space-x-4">
          <FunnelIcon className="h-5 w-5 text-gray-500" />
          <select
            value={filters.stream}
            onChange={(e) => setFilters({...filters, stream: e.target.value})}
            className="border rounded px-3 py-2"
          >
            <option value="">All Streams</option>
            {STREAMS.map(stream => (
              <option key={stream} value={stream}>{stream}</option>
            ))}
          </select>
          <select
            value={filters.story_type}
            onChange={(e) => setFilters({...filters, story_type: e.target.value})}
            className="border rounded px-3 py-2"
          >
            <option value="">All Story Types</option>
            {STORY_TYPES.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Stories List */}
      {loading ? (
        <div className="text-center py-8">Loading stories...</div>
      ) : stories.length === 0 ? (
        <div className="bg-white rounded-lg p-8 text-center shadow">
          <ChatBubbleLeftRightIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No stories yet</h3>
          <p className="text-gray-600 mb-4">Be the first to share your AAIP success story!</p>
          <button
            onClick={() => setShowSubmitForm(true)}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition"
          >
            Share Your Story
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {stories.map((story) => {
            const StoryIcon = STORY_TYPES.find(t => t.value === story.story_type)?.icon || TrophyIcon;
            const daysToNomination = calculateDuration(story.timeline_submitted, story.timeline_nominated);
            
            return (
              <div key={story.id} className="bg-white rounded-lg p-6 shadow hover:shadow-md transition">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start space-x-3">
                    <div className="bg-green-100 p-3 rounded-lg">
                      <StoryIcon className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">
                        {STORY_TYPES.find(t => t.value === story.story_type)?.label}
                      </h3>
                      <div className="flex items-center space-x-3 text-sm text-gray-600">
                        <span className="font-medium">{story.aaip_stream}</span>
                        {story.noc_code && <span>• NOC {story.noc_code}</span>}
                        {story.city && <span>• {story.city}</span>}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-500">
                      {new Date(story.approved_at).toLocaleDateString()}
                    </div>
                    <div className="text-xs text-gray-400">by {story.author_name}</div>
                  </div>
                </div>

                {/* Timeline */}
                {(story.timeline_submitted || story.timeline_nominated || story.timeline_pr_approved) && (
                  <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                    <div className="text-sm font-medium text-blue-900 mb-2">Timeline</div>
                    <div className="flex flex-wrap gap-4 text-sm">
                      {story.timeline_submitted && (
                        <div>
                          <span className="text-gray-600">Submitted:</span>{' '}
                          <span className="font-medium">{new Date(story.timeline_submitted).toLocaleDateString()}</span>
                        </div>
                      )}
                      {story.timeline_nominated && (
                        <div>
                          <span className="text-gray-600">Nominated:</span>{' '}
                          <span className="font-medium">{new Date(story.timeline_nominated).toLocaleDateString()}</span>
                          {daysToNomination && (
                            <span className="text-green-600 ml-2">({daysToNomination} days)</span>
                          )}
                        </div>
                      )}
                      {story.timeline_pr_approved && (
                        <div>
                          <span className="text-gray-600">PR Approved:</span>{' '}
                          <span className="font-medium">{new Date(story.timeline_pr_approved).toLocaleDateString()}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Story Content */}
                <div className="mb-4">
                  <p className="text-gray-700 whitespace-pre-wrap">{story.story_text}</p>
                </div>

                {/* Tips */}
                {story.tips && (
                  <div className="mb-4 p-3 bg-green-50 rounded-lg">
                    <div className="text-sm font-medium text-green-900 mb-1">💡 Tips</div>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">{story.tips}</p>
                  </div>
                )}

                {/* Challenges */}
                {story.challenges && (
                  <div className="mb-4 p-3 bg-yellow-50 rounded-lg">
                    <div className="text-sm font-medium text-yellow-900 mb-1">⚠️ Challenges</div>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">{story.challenges}</p>
                  </div>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between pt-4 border-t">
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    {story.crs_score && (
                      <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">
                        CRS: {story.crs_score}
                      </span>
                    )}
                    {story.work_permit_type && (
                      <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full">
                        {story.work_permit_type}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => handleMarkHelpful(story.id)}
                    className="flex items-center space-x-2 text-gray-600 hover:text-red-500 transition"
                  >
                    <HeartIcon className="h-5 w-5" />
                    <span className="font-medium">{story.helpful_count || 0} helpful</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default SuccessStories;
