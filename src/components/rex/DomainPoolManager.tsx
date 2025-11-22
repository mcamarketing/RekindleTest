/**
 * DomainPoolManager - Domain Pool Management UI
 *
 * Manages domain rotation pool, warmup progress, health monitoring,
 * and automatic rotation for email deliverability.
 */

import React, { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';

interface Domain {
  id: string;
  domain: string;
  status: 'active' | 'warming' | 'paused' | 'retired';
  warmup_state: 'cold' | 'warming' | 'warm';
  warmup_day: number;
  reputation_score: number;
  bounce_rate: number;
  spam_complaint_rate: number;
  open_rate: number;
  emails_sent_today: number;
  emails_sent_total: number;
  warmup_target_per_day: number;
  last_used_at: string;
  created_at: string;
}

interface DomainHealthMetrics {
  health_status: 'excellent' | 'good' | 'fair' | 'poor' | 'critical';
  deliverability_score: number;
  should_rotate: boolean;
  rotation_reason?: string;
}

export const DomainPoolManager: React.FC = () => {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDomain, setSelectedDomain] = useState<Domain | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newDomain, setNewDomain] = useState('');

  useEffect(() => {
    fetchDomains();
  }, []);

  const fetchDomains = async () => {
    try {
      const { data, error } = await supabase
        .from('rex_domain_pool')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      setDomains(data || []);
    } catch (error) {
      console.error('Error fetching domains:', error);
    } finally {
      setLoading(false);
    }
  };

  const addDomain = async () => {
    if (!newDomain) return;

    try {
      const { data, error } = await supabase
        .from('rex_domain_pool')
        .insert({
          domain: newDomain,
          status: 'active',
          warmup_state: 'cold',
          warmup_day: 0,
          reputation_score: 1.0,
          bounce_rate: 0.0,
          spam_complaint_rate: 0.0,
          open_rate: 0.0,
          emails_sent_today: 0,
          emails_sent_total: 0,
          warmup_target_per_day: 10, // Start with 10 emails/day
        })
        .select()
        .single();

      if (error) throw error;

      setDomains([data, ...domains]);
      setNewDomain('');
      setShowAddModal(false);
    } catch (error) {
      console.error('Error adding domain:', error);
    }
  };

  const pauseDomain = async (domainId: string) => {
    try {
      const { error } = await supabase
        .from('rex_domain_pool')
        .update({ status: 'paused' })
        .eq('id', domainId);

      if (error) throw error;
      fetchDomains();
    } catch (error) {
      console.error('Error pausing domain:', error);
    }
  };

  const resumeDomain = async (domainId: string) => {
    try {
      const { error } = await supabase
        .from('rex_domain_pool')
        .update({ status: 'active' })
        .eq('id', domainId);

      if (error) throw error;
      fetchDomains();
    } catch (error) {
      console.error('Error resuming domain:', error);
    }
  };

  const getHealthStatus = (domain: Domain): DomainHealthMetrics => {
    const deliverabilityScore =
      domain.reputation_score * 0.4 +
      Math.max(0, 1 - domain.bounce_rate / 0.1) * 0.3 +
      Math.max(0, 1 - domain.spam_complaint_rate / 0.01) * 0.2 +
      domain.open_rate * 0.1;

    let health_status: DomainHealthMetrics['health_status'] = 'excellent';
    if (deliverabilityScore < 0.5) health_status = 'critical';
    else if (deliverabilityScore < 0.7) health_status = 'poor';
    else if (deliverabilityScore < 0.8) health_status = 'fair';
    else if (deliverabilityScore < 0.9) health_status = 'good';

    const should_rotate =
      domain.reputation_score < 0.7 ||
      domain.bounce_rate > 0.05 ||
      domain.spam_complaint_rate > 0.001 ||
      deliverabilityScore < 0.8;

    return {
      health_status,
      deliverability_score: deliverabilityScore,
      should_rotate,
      rotation_reason: should_rotate
        ? domain.reputation_score < 0.7
          ? 'Low reputation'
          : domain.bounce_rate > 0.05
          ? 'High bounce rate'
          : 'Low deliverability'
        : undefined,
    };
  };

  const getWarmupProgress = (domain: Domain): number => {
    if (domain.warmup_state === 'warm') return 100;
    if (domain.warmup_state === 'cold') return 0;
    return Math.min(100, (domain.warmup_day / 14) * 100);
  };

  const getHealthColor = (status: string): string => {
    switch (status) {
      case 'excellent':
        return 'text-green-600';
      case 'good':
        return 'text-blue-600';
      case 'fair':
        return 'text-yellow-600';
      case 'poor':
        return 'text-orange-600';
      case 'critical':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading domains...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Domain Pool</h2>
          <p className="text-gray-600 mt-1">
            Manage email domains for deliverability and rotation
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Add Domain
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600">Total Domains</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">
            {domains.length}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600">Active & Warm</div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {
              domains.filter(
                (d) => d.status === 'active' && d.warmup_state === 'warm'
              ).length
            }
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600">Warming Up</div>
          <div className="text-2xl font-bold text-yellow-600 mt-1">
            {domains.filter((d) => d.warmup_state === 'warming').length}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600">Needs Attention</div>
          <div className="text-2xl font-bold text-red-600 mt-1">
            {
              domains.filter((d) => {
                const health = getHealthStatus(d);
                return health.should_rotate;
              }).length
            }
          </div>
        </div>
      </div>

      {/* Domain List */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Domain
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Health
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Warmup
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Metrics
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {domains.map((domain) => {
              const health = getHealthStatus(domain);
              const warmupProgress = getWarmupProgress(domain);

              return (
                <tr
                  key={domain.id}
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => setSelectedDomain(domain)}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {domain.domain}
                    </div>
                    <div className="text-xs text-gray-500">
                      {domain.emails_sent_total.toLocaleString()} emails sent
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        domain.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : domain.status === 'warming'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {domain.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div
                      className={`text-sm font-medium ${getHealthColor(
                        health.health_status
                      )}`}
                    >
                      {health.health_status.charAt(0).toUpperCase() +
                        health.health_status.slice(1)}
                    </div>
                    <div className="text-xs text-gray-500">
                      Score: {(health.deliverability_score * 100).toFixed(0)}%
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${warmupProgress}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {domain.warmup_state === 'warm'
                        ? 'Fully warmed'
                        : `Day ${domain.warmup_day}/14`}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div>Bounce: {(domain.bounce_rate * 100).toFixed(1)}%</div>
                    <div>Open: {(domain.open_rate * 100).toFixed(1)}%</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {domain.status === 'active' ? (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          pauseDomain(domain.id);
                        }}
                        className="text-yellow-600 hover:text-yellow-900"
                      >
                        Pause
                      </button>
                    ) : (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          resumeDomain(domain.id);
                        }}
                        className="text-green-600 hover:text-green-900"
                      >
                        Resume
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Add Domain Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Add New Domain
            </h3>
            <input
              type="text"
              value={newDomain}
              onChange={(e) => setNewDomain(e.target.value)}
              placeholder="example.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4"
            />
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={addDomain}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Add Domain
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Domain Detail Modal */}
      {selectedDomain && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  {selectedDomain.domain}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  Domain Details & Health Metrics
                </p>
              </div>
              <button
                onClick={() => setSelectedDomain(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4">
              {/* Health Metrics */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-3">
                  Health Metrics
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-600">Reputation Score</div>
                    <div className="text-lg font-bold text-gray-900">
                      {(selectedDomain.reputation_score * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Bounce Rate</div>
                    <div className="text-lg font-bold text-gray-900">
                      {(selectedDomain.bounce_rate * 100).toFixed(2)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Spam Rate</div>
                    <div className="text-lg font-bold text-gray-900">
                      {(selectedDomain.spam_complaint_rate * 100).toFixed(3)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Open Rate</div>
                    <div className="text-lg font-bold text-gray-900">
                      {(selectedDomain.open_rate * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>

              {/* Warmup Progress */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-3">
                  Warmup Progress
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Day {selectedDomain.warmup_day} of 14</span>
                    <span className="font-medium">{selectedDomain.warmup_state}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-blue-600 h-3 rounded-full transition-all"
                      style={{ width: `${getWarmupProgress(selectedDomain)}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>Today: {selectedDomain.emails_sent_today}/{selectedDomain.warmup_target_per_day}</span>
                    <span>Total: {selectedDomain.emails_sent_total.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>

            <button
              onClick={() => setSelectedDomain(null)}
              className="mt-6 w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
