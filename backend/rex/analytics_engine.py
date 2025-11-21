"""
REX Analytics Engine
Real-time metrics collection, trend analysis, and performance monitoring
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsSnapshot:
    """Point-in-time analytics snapshot"""
    timestamp: datetime

    missions: Dict[str, Any]
    agents: Dict[str, Dict[str, Any]]
    campaigns: Dict[str, Any]
    domains: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'missions': self.missions,
            'agents': self.agents,
            'campaigns': self.campaigns,
            'domains': self.domains
        }


@dataclass
class TrendData:
    """Trend data over time period"""
    missions_per_hour: List[int]
    success_rate: List[float]
    avg_duration_ms: List[float]
    domain_reputation_avg: List[float]
    api_usage: Dict[str, List[int]]


class AnalyticsEngine:
    """
    Collects real-time metrics and generates analytics snapshots.
    Provides trend analysis and performance benchmarking.
    """

    # Snapshot intervals
    SNAPSHOT_INTERVAL = 3600  # 1 hour in seconds
    REAL_TIME_INTERVAL = 5  # 5 seconds for real-time metrics

    # Benchmark targets
    BENCHMARK_TARGETS = {
        'mission_success_rate': 0.95,  # 95% success rate
        'avg_mission_duration_ms': 300000,  # 5 minutes
        'domain_reputation_avg': 0.85,  # 85% average reputation
        'agent_utilization': 0.70,  # 70% agent utilization
        'reply_rate': 0.30,  # 30% reply rate
        'meeting_rate': 0.10,  # 10% meeting booking rate
    }

    def __init__(self, db, redis):
        self.db = db
        self.redis = redis

        # In-memory cache for real-time metrics
        self.current_metrics: Dict[str, Any] = {}
        self.snapshot_history: List[AnalyticsSnapshot] = []

        # Anomaly detection thresholds
        self.anomaly_thresholds = {
            'success_rate_drop': 0.20,  # 20% drop triggers alert
            'duration_spike': 2.0,  # 2x avg duration triggers alert
            'domain_reputation_drop': 0.15,  # 15% drop triggers alert
        }

    async def start(self):
        """Start analytics collection loops"""
        logger.info("Starting analytics engine...")

        await asyncio.gather(
            self._real_time_metrics_loop(),
            self._snapshot_loop(),
            self._anomaly_detection_loop()
        )

    async def _real_time_metrics_loop(self):
        """Collect real-time metrics every 5 seconds"""
        while True:
            try:
                await self._collect_real_time_metrics()
                await asyncio.sleep(self.REAL_TIME_INTERVAL)
            except Exception as e:
                logger.error(f"Error in real-time metrics loop: {e}")
                await asyncio.sleep(self.REAL_TIME_INTERVAL)

    async def _snapshot_loop(self):
        """Generate analytics snapshots every hour"""
        while True:
            try:
                snapshot = await self.generate_snapshot()
                await self._persist_snapshot(snapshot)

                # Keep last 24 hours in memory
                self.snapshot_history.append(snapshot)
                if len(self.snapshot_history) > 24:
                    self.snapshot_history.pop(0)

                logger.info(f"Analytics snapshot generated: {snapshot.timestamp}")
                await asyncio.sleep(self.SNAPSHOT_INTERVAL)
            except Exception as e:
                logger.error(f"Error in snapshot loop: {e}")
                await asyncio.sleep(self.SNAPSHOT_INTERVAL)

    async def _anomaly_detection_loop(self):
        """Check for performance anomalies every 5 minutes"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                anomalies = await self.detect_anomalies()

                if anomalies:
                    logger.warning(f"Performance anomalies detected: {anomalies}")
                    await self._alert_anomalies(anomalies)
            except Exception as e:
                logger.error(f"Error in anomaly detection loop: {e}")

    async def _collect_real_time_metrics(self):
        """Collect real-time metrics from database"""
        try:
            # Mission counts by state
            mission_result = await self.db.table('rex_missions') \
                .select('state', count='exact') \
                .execute()

            mission_counts = {}
            for row in mission_result.data:
                mission_counts[row['state']] = mission_counts.get(row['state'], 0) + 1

            # Active missions
            active_count = sum(
                mission_counts.get(state, 0)
                for state in ['assigned', 'executing', 'collecting', 'analyzing', 'optimizing']
            )

            # Success rate (last 1 hour)
            one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
            recent_missions = await self.db.table('rex_missions') \
                .select('state') \
                .gte('completed_at', one_hour_ago) \
                .execute()

            total_recent = len(recent_missions.data)
            completed_recent = len([m for m in recent_missions.data if m['state'] == 'completed'])
            success_rate = completed_recent / total_recent if total_recent > 0 else 0.0

            # Update cache
            self.current_metrics = {
                'active_missions': active_count,
                'queued_missions': mission_counts.get('queued', 0),
                'completed_24h': completed_recent,
                'failed_24h': len([m for m in recent_missions.data if m['state'] == 'failed']),
                'success_rate': success_rate,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Store in Redis for fast access
            await self.redis.set(
                'rex:metrics:realtime',
                str(self.current_metrics),
                ex=60  # Expire after 1 minute
            )

        except Exception as e:
            logger.error(f"Error collecting real-time metrics: {e}")

    async def generate_snapshot(self) -> AnalyticsSnapshot:
        """Generate comprehensive analytics snapshot"""
        try:
            timestamp = datetime.utcnow()

            # Mission analytics
            missions = await self._collect_mission_analytics()

            # Agent analytics
            agents = await self._collect_agent_analytics()

            # Campaign analytics
            campaigns = await self._collect_campaign_analytics()

            # Domain analytics
            domains = await self._collect_domain_analytics()

            return AnalyticsSnapshot(
                timestamp=timestamp,
                missions=missions,
                agents=agents,
                campaigns=campaigns,
                domains=domains
            )

        except Exception as e:
            logger.error(f"Error generating snapshot: {e}")
            return AnalyticsSnapshot(
                timestamp=datetime.utcnow(),
                missions={},
                agents={},
                campaigns={},
                domains={}
            )

    async def _collect_mission_analytics(self) -> Dict[str, Any]:
        """Collect mission-related analytics"""
        try:
            # All missions
            all_missions = await self.db.table('rex_missions') \
                .select('state, completed_at, started_at, created_at, metrics') \
                .execute()

            total = len(all_missions.data)
            active = len([m for m in all_missions.data if m['state'] in [
                'assigned', 'executing', 'collecting', 'analyzing', 'optimizing'
            ]])
            completed = len([m for m in all_missions.data if m['state'] == 'completed'])
            failed = len([m for m in all_missions.data if m['state'] == 'failed'])

            # Average duration (completed missions only)
            durations = []
            for mission in all_missions.data:
                if mission.get('metrics') and mission['metrics'].get('duration_ms'):
                    durations.append(mission['metrics']['duration_ms'])

            avg_duration = sum(durations) / len(durations) if durations else 0

            return {
                'total': total,
                'active': active,
                'completed': completed,
                'failed': failed,
                'avg_duration_ms': avg_duration
            }

        except Exception as e:
            logger.error(f"Error collecting mission analytics: {e}")
            return {'total': 0, 'active': 0, 'completed': 0, 'failed': 0, 'avg_duration_ms': 0}

    async def _collect_agent_analytics(self) -> Dict[str, Dict[str, Any]]:
        """Collect agent-related analytics by crew"""
        try:
            # Tasks grouped by agent
            tasks = await self.db.table('rex_tasks') \
                .select('agent_name, state, duration_ms, created_at') \
                .execute()

            agent_stats: Dict[str, Dict[str, Any]] = {}

            for task in tasks.data:
                agent = task['agent_name']
                if agent not in agent_stats:
                    agent_stats[agent] = {
                        'executions': 0,
                        'completed': 0,
                        'failed': 0,
                        'durations': []
                    }

                agent_stats[agent]['executions'] += 1

                if task['state'] == 'completed':
                    agent_stats[agent]['completed'] += 1
                elif task['state'] == 'failed':
                    agent_stats[agent]['failed'] += 1

                if task.get('duration_ms'):
                    agent_stats[agent]['durations'].append(task['duration_ms'])

            # Calculate success rates and avg durations
            result = {}
            for agent, stats in agent_stats.items():
                executions = stats['executions']
                result[agent] = {
                    'executions': executions,
                    'success_rate': stats['completed'] / executions if executions > 0 else 0.0,
                    'avg_duration_ms': sum(stats['durations']) / len(stats['durations']) if stats['durations'] else 0,
                    'error_count': stats['failed']
                }

            return result

        except Exception as e:
            logger.error(f"Error collecting agent analytics: {e}")
            return {}

    async def _collect_campaign_analytics(self) -> Dict[str, Any]:
        """Collect campaign performance analytics"""
        try:
            # This would integrate with campaigns table
            # For now, return placeholder structure
            return {
                'total_leads': 0,
                'contacted': 0,
                'replied': 0,
                'meetings_booked': 0,
                'reply_rate': 0.0,
                'meeting_rate': 0.0
            }

        except Exception as e:
            logger.error(f"Error collecting campaign analytics: {e}")
            return {
                'total_leads': 0,
                'contacted': 0,
                'replied': 0,
                'meetings_booked': 0,
                'reply_rate': 0.0,
                'meeting_rate': 0.0
            }

    async def _collect_domain_analytics(self) -> Dict[str, Any]:
        """Collect domain health analytics"""
        try:
            domains = await self.db.table('rex_domain_pool') \
                .select('reputation_score, status, rotated_at') \
                .execute()

            reputation_scores = [d['reputation_score'] for d in domains.data if d.get('reputation_score')]
            avg_reputation = sum(reputation_scores) / len(reputation_scores) if reputation_scores else 0.0

            # Count rotation events in last 24 hours
            one_day_ago = (datetime.utcnow() - timedelta(days=1)).isoformat()
            rotation_events = len([
                d for d in domains.data
                if d.get('rotated_at') and d['rotated_at'] >= one_day_ago
            ])

            warmup_in_progress = len([
                d for d in domains.data
                if d.get('status') == 'warming'
            ])

            return {
                'reputation_avg': avg_reputation,
                'rotation_events': rotation_events,
                'warmup_in_progress': warmup_in_progress
            }

        except Exception as e:
            logger.error(f"Error collecting domain analytics: {e}")
            return {
                'reputation_avg': 0.0,
                'rotation_events': 0,
                'warmup_in_progress': 0
            }

    async def _persist_snapshot(self, snapshot: AnalyticsSnapshot):
        """Persist snapshot to database"""
        try:
            await self.db.table('rex_analytics').insert({
                'timestamp': snapshot.timestamp.isoformat(),
                'missions': snapshot.missions,
                'agents': snapshot.agents,
                'campaigns': snapshot.campaigns,
                'domains': snapshot.domains
            }).execute()

            logger.info(f"Snapshot persisted: {snapshot.timestamp}")

        except Exception as e:
            logger.error(f"Error persisting snapshot: {e}")

    async def get_trends(self, hours: int = 24) -> TrendData:
        """Get trend data for the last N hours"""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)

            # Fetch snapshots from database
            snapshots = await self.db.table('rex_analytics') \
                .select('*') \
                .gte('timestamp', cutoff.isoformat()) \
                .order('timestamp', desc=False) \
                .execute()

            # Extract trends
            missions_per_hour = []
            success_rates = []
            avg_durations = []
            domain_reputations = []

            for snapshot in snapshots.data:
                missions = snapshot.get('missions', {})
                domains = snapshot.get('domains', {})

                missions_per_hour.append(missions.get('completed', 0))

                total = missions.get('total', 0)
                completed = missions.get('completed', 0)
                success_rate = completed / total if total > 0 else 0.0
                success_rates.append(success_rate)

                avg_durations.append(missions.get('avg_duration_ms', 0))
                domain_reputations.append(domains.get('reputation_avg', 0.0))

            return TrendData(
                missions_per_hour=missions_per_hour,
                success_rate=success_rates,
                avg_duration_ms=avg_durations,
                domain_reputation_avg=domain_reputations,
                api_usage={}  # TODO: Implement API usage tracking
            )

        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            return TrendData(
                missions_per_hour=[],
                success_rate=[],
                avg_duration_ms=[],
                domain_reputation_avg=[],
                api_usage={}
            )

    async def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect performance anomalies"""
        anomalies = []

        try:
            # Get recent trends (last 6 hours)
            trends = await self.get_trends(hours=6)

            if not trends.success_rate:
                return anomalies

            # Check success rate drop
            current_success = trends.success_rate[-1] if trends.success_rate else 0.0
            avg_success = sum(trends.success_rate) / len(trends.success_rate) if trends.success_rate else 0.0

            if current_success < avg_success - self.anomaly_thresholds['success_rate_drop']:
                anomalies.append({
                    'type': 'success_rate_drop',
                    'severity': 'high',
                    'current': current_success,
                    'expected': avg_success,
                    'message': f'Success rate dropped to {current_success:.2%} (expected: {avg_success:.2%})'
                })

            # Check duration spike
            current_duration = trends.avg_duration_ms[-1] if trends.avg_duration_ms else 0
            avg_duration = sum(trends.avg_duration_ms) / len(trends.avg_duration_ms) if trends.avg_duration_ms else 0

            if current_duration > avg_duration * self.anomaly_thresholds['duration_spike']:
                anomalies.append({
                    'type': 'duration_spike',
                    'severity': 'medium',
                    'current': current_duration,
                    'expected': avg_duration,
                    'message': f'Mission duration spiked to {current_duration}ms (expected: {avg_duration}ms)'
                })

            # Check domain reputation drop
            current_reputation = trends.domain_reputation_avg[-1] if trends.domain_reputation_avg else 0.0
            avg_reputation = sum(trends.domain_reputation_avg) / len(trends.domain_reputation_avg) if trends.domain_reputation_avg else 0.0

            if current_reputation < avg_reputation - self.anomaly_thresholds['domain_reputation_drop']:
                anomalies.append({
                    'type': 'domain_reputation_drop',
                    'severity': 'high',
                    'current': current_reputation,
                    'expected': avg_reputation,
                    'message': f'Domain reputation dropped to {current_reputation:.2f} (expected: {avg_reputation:.2f})'
                })

            return anomalies

        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []

    async def _alert_anomalies(self, anomalies: List[Dict[str, Any]]):
        """Send alerts for detected anomalies"""
        try:
            for anomaly in anomalies:
                # Log to rex_logs
                await self.db.table('rex_logs').insert({
                    'user_id': 'system',
                    'level': 'warning' if anomaly['severity'] == 'medium' else 'error',
                    'message': anomaly['message'],
                    'context': anomaly,
                    'source': 'analytics_engine'
                }).execute()

                # Publish to Redis for real-time alerts
                await self.redis.publish(
                    'rex:alerts:anomalies',
                    str(anomaly)
                )

            logger.warning(f"Anomaly alerts sent: {len(anomalies)} anomalies")

        except Exception as e:
            logger.error(f"Error alerting anomalies: {e}")

    async def get_performance_benchmarks(self) -> Dict[str, Any]:
        """Compare current performance against benchmarks"""
        try:
            # Get current snapshot
            snapshot = await self.generate_snapshot()

            missions = snapshot.missions
            domains = snapshot.domains

            # Calculate current metrics
            total_missions = missions.get('total', 0)
            completed_missions = missions.get('completed', 0)
            current_success_rate = completed_missions / total_missions if total_missions > 0 else 0.0
            current_avg_duration = missions.get('avg_duration_ms', 0)
            current_domain_reputation = domains.get('reputation_avg', 0.0)

            # Compare to benchmarks
            return {
                'success_rate': {
                    'current': current_success_rate,
                    'target': self.BENCHMARK_TARGETS['mission_success_rate'],
                    'status': 'on_target' if current_success_rate >= self.BENCHMARK_TARGETS['mission_success_rate'] else 'below_target',
                    'delta': current_success_rate - self.BENCHMARK_TARGETS['mission_success_rate']
                },
                'avg_duration_ms': {
                    'current': current_avg_duration,
                    'target': self.BENCHMARK_TARGETS['avg_mission_duration_ms'],
                    'status': 'on_target' if current_avg_duration <= self.BENCHMARK_TARGETS['avg_mission_duration_ms'] else 'above_target',
                    'delta': current_avg_duration - self.BENCHMARK_TARGETS['avg_mission_duration_ms']
                },
                'domain_reputation': {
                    'current': current_domain_reputation,
                    'target': self.BENCHMARK_TARGETS['domain_reputation_avg'],
                    'status': 'on_target' if current_domain_reputation >= self.BENCHMARK_TARGETS['domain_reputation_avg'] else 'below_target',
                    'delta': current_domain_reputation - self.BENCHMARK_TARGETS['domain_reputation_avg']
                }
            }

        except Exception as e:
            logger.error(f"Error getting performance benchmarks: {e}")
            return {}

    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get cached real-time metrics"""
        return self.current_metrics.copy()

    async def get_snapshot_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get snapshot history from memory or database"""
        if hours <= 24 and self.snapshot_history:
            # Return from memory cache
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            return [
                s.to_dict()
                for s in self.snapshot_history
                if s.timestamp >= cutoff
            ]
        else:
            # Fetch from database
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            result = await self.db.table('rex_analytics') \
                .select('*') \
                .gte('timestamp', cutoff.isoformat()) \
                .order('timestamp', desc=False) \
                .execute()

            return result.data
