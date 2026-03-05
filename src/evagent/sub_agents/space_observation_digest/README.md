# Space Observation Digest Sub-Agent

This sub-agent delivers a daily digest of recent papers about event cameras for space observation.

Features:
- fetches papers from the existing multi-source retriever
- ranks by publication recency and relevance
- outputs title + main content summary
- writes daily digest files under `output/sub_agents/space_observation_digest/`
- can send local desktop notifications (Linux/macOS)

