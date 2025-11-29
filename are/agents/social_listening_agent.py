"""
ARE Social Listening Agent

Continuously gathers market intelligence from social platforms to inform
revenue strategies. Performs sentiment analysis, topic modeling, and
extracts actionable insights about customer pain points and preferences.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class SocialInsight:
    """Represents a processed social media insight"""
    id: str
    source: str  # 'reddit', 'forum', etc.
    topic: str
    sentiment: str  # 'positive', 'negative', 'neutral'
    pain_points: List[str]
    desires: List[str]
    objections: List[str]
    confidence_score: float
    timestamp: datetime
    anonymized_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MarketIntelligence:
    """Aggregated market intelligence report"""
    report_id: str
    time_period: str
    insights: List[SocialInsight]
    top_pain_points: List[str]
    top_desires: List[str]
    sentiment_trends: Dict[str, float]
    actionable_recommendations: List[str]
    generated_at: datetime

class SocialListeningAgent:
    """ARE Social Listening Agent - Continuous market intelligence gathering"""

    def __init__(self):
        self.sources = {
            'reddit': {
                'subreddits': ['r/sales', 'r/marketing', 'r/smallbusiness', 'r/entrepreneur'],
                'api_endpoint': 'https://www.reddit.com/r/{subreddit}/new.json',
                'rate_limit': 60,  # requests per minute
            },
            'forums': {
                'sites': ['hackernews', 'indiehackers'],
                'rate_limit': 30,
            }
        }
        self.collection_interval = 3600  # 1 hour
        self.is_running = False
        self.last_collection = None
        self.insights_buffer: List[SocialInsight] = []
        self.privacy_filters = self._load_privacy_filters()

    def _load_privacy_filters(self) -> List[str]:
        """Load privacy and content filters"""
        return [
            r'\b\d{3,}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP addresses
            r'\b(?:\d{4}[-\s]?){3}\d{4}\b',  # Credit cards
            r'\b\w{2,}\s+\w{2,}\s+\d{1,5}\b',  # Addresses
        ]

    async def run(self, input_data: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Main execution method - can run on-demand or continuously"""
        mode = input_data.get('mode', 'continuous')

        if mode == 'continuous':
            return await self._run_continuous()
        elif mode == 'on_demand':
            return await self._run_on_demand(input_data)
        else:
            raise ValueError(f"Unknown mode: {mode}")

    async def _run_continuous(self) -> Dict[str, Any]:
        """Run continuous social listening"""
        logger.info("Starting continuous social listening...")

        self.is_running = True
        collection_count = 0

        try:
            while self.is_running:
                await self._collect_intelligence()
                collection_count += 1

                # Generate periodic reports
                if collection_count % 6 == 0:  # Every 6 hours
                    await self._generate_market_report()

                await asyncio.sleep(self.collection_interval)

        except Exception as e:
            logger.error(f"Continuous listening failed: {e}")
            self.is_running = False

        return {"status": "stopped", "collections": collection_count}

    async def _run_on_demand(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run on-demand intelligence collection"""
        logger.info("Running on-demand social intelligence collection...")

        sources = input_data.get('sources', ['reddit'])
        topics = input_data.get('topics', [])

        await self._collect_intelligence(sources=sources, topics=topics)
        report = await self._generate_market_report()

        return {
            "status": "completed",
            "insights_collected": len(self.insights_buffer),
            "report": report
        }

    async def _collect_intelligence(self, sources: Optional[List[str]] = None, topics: Optional[List[str]] = None):
        """Collect intelligence from configured sources"""
        if sources is None:
            sources = list(self.sources.keys())

        logger.info(f"Collecting intelligence from sources: {sources}")

        for source in sources:
            try:
                if source == 'reddit':
                    await self._collect_from_reddit(topics)
                elif source == 'forums':
                    await self._collect_from_forums(topics)
                else:
                    logger.warning(f"Unknown source: {source}")

            except Exception as e:
                logger.error(f"Failed to collect from {source}: {e}")

        self.last_collection = datetime.now()

    async def _collect_from_reddit(self, topics: Optional[List[str]] = None):
        """Collect posts from Reddit using official API"""
        # Note: In production, this would use proper Reddit API authentication
        # For now, using mock data structure

        for subreddit in self.sources['reddit']['subreddits']:
            logger.debug(f"Collecting from r/{subreddit}")

            # Mock API call - replace with actual Reddit API
            mock_posts = self._get_mock_reddit_posts(subreddit)

            for post in mock_posts:
                insight = await self._process_post(post, 'reddit')
                if insight:
                    self.insights_buffer.append(insight)

            # Respect rate limits
            await asyncio.sleep(1)

    async def _collect_from_forums(self, topics: Optional[List[str]] = None):
        """Collect from business forums"""
        # Mock implementation - replace with actual forum APIs
        logger.debug("Collecting from forums")

        mock_posts = self._get_mock_forum_posts()
        for post in mock_posts:
            insight = await self._process_post(post, 'forum')
            if insight:
                self.insights_buffer.append(insight)

    async def _process_post(self, post: Dict[str, Any], source: str) -> Optional[SocialInsight]:
        """Process a social media post into insights"""
        try:
            # Anonymize content
            anonymized_content = self._anonymize_content(post.get('text', ''))

            # Skip if content is too short or filtered
            if len(anonymized_content) < 20:
                return None

            # Extract insights using NLP
            sentiment = await self._analyze_sentiment(anonymized_content)
            topics = await self._extract_topics(anonymized_content)
            pain_points = await self._extract_pain_points(anonymized_content)
            desires = await self._extract_desires(anonymized_content)
            objections = await self._extract_objections(anonymized_content)

            # Calculate confidence score
            confidence = self._calculate_confidence(sentiment, topics, pain_points, desires, objections)

            if confidence < 0.3:  # Low confidence insights are not useful
                return None

            insight = SocialInsight(
                id=f"{source}_{post.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source=source,
                topic=topics[0] if topics else 'general',
                sentiment=sentiment,
                pain_points=pain_points,
                desires=desires,
                objections=objections,
                confidence_score=confidence,
                timestamp=datetime.now(),
                anonymized_content=anonymized_content,
                metadata={
                    'original_length': len(post.get('text', '')),
                    'upvotes': post.get('upvotes', 0),
                    'comments': post.get('comments', 0)
                }
            )

            return insight

        except Exception as e:
            logger.error(f"Failed to process post: {e}")
            return None

    def _anonymize_content(self, content: str) -> str:
        """Remove personally identifiable information"""
        anonymized = content

        for pattern in self.privacy_filters:
            anonymized = re.sub(pattern, '[REDACTED]', anonymized)

        return anonymized

    async def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        # Mock sentiment analysis - replace with actual NLP model
        positive_words = ['great', 'awesome', 'love', 'excellent', 'amazing', 'perfect']
        negative_words = ['hate', 'terrible', 'awful', 'worst', 'sucks', 'horrible']

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    async def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
        # Mock topic extraction - replace with actual NLP
        topics = []
        text_lower = text.lower()

        topic_keywords = {
            'sales': ['sales', 'selling', 'revenue', 'customers', 'leads'],
            'marketing': ['marketing', 'advertising', 'campaign', 'brand'],
            'pricing': ['pricing', 'cost', 'expensive', 'cheap', 'budget'],
            'support': ['support', 'help', 'service', 'customer service'],
            'product': ['product', 'features', 'quality', 'reliability']
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return topics[:3]  # Limit to top 3 topics

    async def _extract_pain_points(self, text: str) -> List[str]:
        """Extract customer pain points"""
        # Mock extraction - replace with actual NLP
        pain_indicators = ['problem', 'issue', 'frustrated', 'difficult', 'hard', 'struggle']
        text_lower = text.lower()

        pains = []
        if any(indicator in text_lower for indicator in pain_indicators):
            # Extract sentences containing pain indicators
            sentences = text.split('.')
            for sentence in sentences:
                if any(indicator in sentence.lower() for indicator in pain_indicators):
                    pains.append(sentence.strip())

        return pains[:5]  # Limit to 5 pain points

    async def _extract_desires(self, text: str) -> List[str]:
        """Extract customer desires and wishes"""
        # Mock extraction
        desire_indicators = ['want', 'need', 'wish', 'hope', 'looking for', 'seeking']
        text_lower = text.lower()

        desires = []
        if any(indicator in text_lower for indicator in desire_indicators):
            sentences = text.split('.')
            for sentence in sentences:
                if any(indicator in sentence.lower() for indicator in desire_indicators):
                    desires.append(sentence.strip())

        return desires[:5]

    async def _extract_objections(self, text: str) -> List[str]:
        """Extract common objections"""
        # Mock extraction
        objection_indicators = ['but', 'however', 'concern', 'worry', 'skeptical']
        text_lower = text.lower()

        objections = []
        if any(indicator in text_lower for indicator in objection_indicators):
            sentences = text.split('.')
            for sentence in sentences:
                if any(indicator in sentence.lower() for indicator in objection_indicators):
                    objections.append(sentence.strip())

        return objections[:5]

    def _calculate_confidence(self, sentiment: str, topics: List[str], pains: List[str],
                            desires: List[str], objections: List[str]) -> float:
        """Calculate confidence score for insights"""
        score = 0.0

        if sentiment != 'neutral':
            score += 0.2

        if topics:
            score += 0.3

        if pains:
            score += 0.2

        if desires:
            score += 0.15

        if objections:
            score += 0.15

        return min(score, 1.0)

    async def _generate_market_report(self) -> MarketIntelligence:
        """Generate aggregated market intelligence report"""
        if not self.insights_buffer:
            return None

        # Aggregate insights from last 24 hours
        recent_insights = [
            insight for insight in self.insights_buffer
            if (datetime.now() - insight.timestamp).total_seconds() < 86400
        ]

        # Calculate sentiment trends
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for insight in recent_insights:
            sentiment_counts[insight.sentiment] += 1

        total = len(recent_insights)
        sentiment_trends = {
            sentiment: count / total if total > 0 else 0
            for sentiment, count in sentiment_counts.items()
        }

        # Aggregate pain points and desires
        all_pain_points = []
        all_desires = []

        for insight in recent_insights:
            all_pain_points.extend(insight.pain_points)
            all_desires.extend(insight.desires)

        # Get top 10 most common
        top_pain_points = self._get_most_common(all_pain_points, 10)
        top_desires = self._get_most_common(all_desires, 10)

        # Generate recommendations
        recommendations = await self._generate_recommendations(sentiment_trends, top_pain_points, top_desires)

        report = MarketIntelligence(
            report_id=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            time_period="last_24_hours",
            insights=recent_insights,
            top_pain_points=top_pain_points,
            top_desires=top_desires,
            sentiment_trends=sentiment_trends,
            actionable_recommendations=recommendations,
            generated_at=datetime.now()
        )

        logger.info(f"Generated market intelligence report with {len(recent_insights)} insights")

        return report

    def _get_most_common(self, items: List[str], limit: int) -> List[str]:
        """Get most common items from list"""
        from collections import Counter
        counter = Counter(items)
        return [item for item, _ in counter.most_common(limit)]

    async def _generate_recommendations(self, sentiment_trends: Dict[str, float],
                                      pain_points: List[str], desires: List[str]) -> List[str]:
        """Generate actionable recommendations from insights"""
        recommendations = []

        # Sentiment-based recommendations
        if sentiment_trends.get('negative', 0) > 0.3:
            recommendations.append("Address negative sentiment in messaging and positioning")

        if sentiment_trends.get('positive', 0) > 0.5:
            recommendations.append("Leverage positive sentiment in testimonials and case studies")

        # Pain point recommendations
        for pain in pain_points[:3]:
            if 'pricing' in pain.lower():
                recommendations.append("Review pricing strategy to address cost concerns")
            elif 'support' in pain.lower():
                recommendations.append("Enhance customer support and onboarding")
            elif 'quality' in pain.lower():
                recommendations.append("Focus on quality improvements and reliability")

        # Desire-based recommendations
        for desire in desires[:3]:
            if 'feature' in desire.lower():
                recommendations.append("Consider adding requested features to product roadmap")
            elif 'integration' in desire.lower():
                recommendations.append("Explore integration partnerships")

        return recommendations

    def _get_mock_reddit_posts(self, subreddit: str) -> List[Dict[str, Any]]:
        """Mock Reddit posts for development - replace with actual API"""
        return [
            {
                'id': f'mock_{subreddit}_1',
                'text': f"Struggling with {subreddit} sales cycles being too long. Any tips?",
                'upvotes': 45,
                'comments': 23
            },
            {
                'id': f'mock_{subreddit}_2',
                'text': f"Love the new features but pricing seems high for small businesses.",
                'upvotes': 67,
                'comments': 34
            }
        ]

    def _get_mock_forum_posts(self) -> List[Dict[str, Any]]:
        """Mock forum posts for development"""
        return [
            {
                'id': 'forum_1',
                'text': "Customer support has been excellent, but I wish there were more integrations.",
                'upvotes': 12,
                'comments': 5
            }
        ]

    async def get_intelligence_summary(self) -> Dict[str, Any]:
        """Get current intelligence summary for RAG service"""
        recent_insights = [
            insight for insight in self.insights_buffer
            if (datetime.now() - insight.timestamp).total_seconds() < 3600  # Last hour
        ]

        return {
            "total_insights": len(self.insights_buffer),
            "recent_insights": len(recent_insights),
            "sentiment_distribution": self._calculate_sentiment_distribution(recent_insights),
            "top_topics": self._get_top_topics(recent_insights),
            "last_collection": self.last_collection.isoformat() if self.last_collection else None
        }

    def _calculate_sentiment_distribution(self, insights: List[SocialInsight]) -> Dict[str, float]:
        """Calculate sentiment distribution"""
        if not insights:
            return {'positive': 0, 'negative': 0, 'neutral': 0}

        sentiments = [insight.sentiment for insight in insights]
        total = len(sentiments)

        return {
            sentiment: sentiments.count(sentiment) / total
            for sentiment in ['positive', 'negative', 'neutral']
        }

    def _get_top_topics(self, insights: List[SocialInsight]) -> List[str]:
        """Get top topics from recent insights"""
        topics = []
        for insight in insights:
            topics.append(insight.topic)

        return self._get_most_common(topics, 5)

    async def stop(self):
        """Stop continuous listening"""
        logger.info("Stopping social listening agent...")
        self.is_running = False