"""
tests/test_consensus_engine.py
=============================================================================
Unit Test Suite for PBFT Multi-Agent Consensus Engine.
Phase 4 - Universal Cognitive Decomposition Engine (UCDE)
=============================================================================
"""

import unittest
from core.consensus_engine import (
    BftConsensusEngine,
    AgentVote,
    ConsensusCertificate,
)


class TestBftConsensusEngine(unittest.TestCase):
    def setUp(self):
        self.engine = BftConsensusEngine()
        self.sample_proposal = {
            "proposal_id": "PROP-ALPHA-01",
            "microservice_architecture": "Event-Driven",
            "active_endpoints": 3,
            "security_clearance": "RESTRICTED",
        }
        self.prop_hash = BftConsensusEngine.compute_artifact_hash(self.sample_proposal)

    def test_pbft_math_invariants(self):
        # N=4 => f = (4-1)//3 = 1 => Quorum = 2f + 1 = 3
        self.assertEqual(self.engine.total_agents, 4)
        self.assertEqual(self.engine.max_tolerated_faults, 1)
        self.assertEqual(self.engine.quorum_required, 3)

    def test_unanimous_consensus_commits(self):
        cert = self.engine.execute_consensus_round("PROP-ALPHA-01", self.sample_proposal)
        self.assertTrue(cert.consensus_reached)
        self.assertEqual(cert.state, "STATE_COMMITTED")
        self.assertEqual(cert.approvals_count, 4)
        self.assertEqual(cert.rejections_count, 0)
        self.assertEqual(cert.byzantine_faults_count, 0)
        self.assertEqual(cert.committed_artifact_hash, self.prop_hash)
        self.assertEqual(len(cert.certificate_seal), 64)

    def test_byzantine_fault_tolerance_with_one_traitor(self):
        # 3 honest agents approve, 1 traitor casts Byzantine fault
        votes = [
            AgentVote(
                agent_id="agent_claude_35",
                model_name="anthropic/claude-3.5-sonnet",
                vote="VOTE_APPROVE",
                artifact_hash=self.prop_hash,
                vote_signature=BftConsensusEngine.sign_vote("agent_claude_35", self.prop_hash, "VOTE_APPROVE"),
            ),
            AgentVote(
                agent_id="agent_gpt_4o",
                model_name="openai/gpt-4o",
                vote="VOTE_APPROVE",
                artifact_hash=self.prop_hash,
                vote_signature=BftConsensusEngine.sign_vote("agent_gpt_4o", self.prop_hash, "VOTE_APPROVE"),
            ),
            AgentVote(
                agent_id="agent_gemini_15",
                model_name="google/gemini-1.5-pro",
                vote="VOTE_APPROVE",
                artifact_hash=self.prop_hash,
                vote_signature=BftConsensusEngine.sign_vote("agent_gemini_15", self.prop_hash, "VOTE_APPROVE"),
            ),
            # Traitor agent (Byzantine)
            AgentVote(
                agent_id="agent_llama_31",
                model_name="meta/llama-3.1-70b-instruct",
                vote="VOTE_BYZANTINE_FAULT",
                artifact_hash=self.prop_hash,
                rationale="Adversarial hallucination attempt",
                vote_signature=BftConsensusEngine.sign_vote("agent_llama_31", self.prop_hash, "VOTE_BYZANTINE_FAULT"),
            ),
        ]

        cert = self.engine.execute_consensus_round("PROP-ALPHA-01", self.sample_proposal, injected_votes=votes)
        # Even with 1 traitor, approvals (3) >= Quorum (3) => Consensus Reached!
        self.assertTrue(cert.consensus_reached)
        self.assertEqual(cert.state, "STATE_COMMITTED")
        self.assertEqual(cert.approvals_count, 3)
        self.assertEqual(cert.byzantine_faults_count, 1)
        self.assertEqual(len(cert.byzantine_incidents), 1)
        self.assertEqual(cert.byzantine_incidents[0].agent_id, "agent_llama_31")

    def test_forged_vote_signature_isolated(self):
        votes = [
            AgentVote(
                agent_id="agent_claude_35",
                model_name="anthropic/claude-3.5-sonnet",
                vote="VOTE_APPROVE",
                artifact_hash=self.prop_hash,
                vote_signature="FORGED_INVALID_SIGNATURE_HEX",  # Forgery!
            ),
            AgentVote(
                agent_id="agent_gpt_4o",
                model_name="openai/gpt-4o",
                vote="VOTE_APPROVE",
                artifact_hash=self.prop_hash,
                vote_signature=BftConsensusEngine.sign_vote("agent_gpt_4o", self.prop_hash, "VOTE_APPROVE"),
            ),
            AgentVote(
                agent_id="agent_gemini_15",
                model_name="google/gemini-1.5-pro",
                vote="VOTE_APPROVE",
                artifact_hash=self.prop_hash,
                vote_signature=BftConsensusEngine.sign_vote("agent_gemini_15", self.prop_hash, "VOTE_APPROVE"),
            ),
            AgentVote(
                agent_id="agent_llama_31",
                model_name="meta/llama-3.1-70b-instruct",
                vote="VOTE_APPROVE",
                artifact_hash=self.prop_hash,
                vote_signature=BftConsensusEngine.sign_vote("agent_llama_31", self.prop_hash, "VOTE_APPROVE"),
            ),
        ]

        cert = self.engine.execute_consensus_round("PROP-ALPHA-01", self.sample_proposal, injected_votes=votes)
        self.assertEqual(cert.byzantine_faults_count, 1)
        self.assertEqual(cert.byzantine_incidents[0].fault_type, "SCHEMA_TAMPERING")
        # 3 honest signatures were valid, so quorum (3) still met
        self.assertTrue(cert.consensus_reached)

    def test_split_brain_hash_mismatch_rejected_when_quorum_lost(self):
        # 2 agents vote on valid hash, 2 agents vote on conflicting hash
        split_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        votes = [
            AgentVote(
                agent_id="agent_claude_35",
                model_name="anthropic/claude-3.5-sonnet",
                vote="VOTE_APPROVE",
                artifact_hash=self.prop_hash,
                vote_signature=BftConsensusEngine.sign_vote("agent_claude_35", self.prop_hash, "VOTE_APPROVE"),
            ),
            AgentVote(
                agent_id="agent_gpt_4o",
                model_name="openai/gpt-4o",
                vote="VOTE_APPROVE",
                artifact_hash=self.prop_hash,
                vote_signature=BftConsensusEngine.sign_vote("agent_gpt_4o", self.prop_hash, "VOTE_APPROVE"),
            ),
            AgentVote(
                agent_id="agent_gemini_15",
                model_name="google/gemini-1.5-pro",
                vote="VOTE_APPROVE",
                artifact_hash=split_hash,  # Conflicting hash
                vote_signature=BftConsensusEngine.sign_vote("agent_gemini_15", split_hash, "VOTE_APPROVE"),
            ),
            AgentVote(
                agent_id="agent_llama_31",
                model_name="meta/llama-3.1-70b-instruct",
                vote="VOTE_APPROVE",
                artifact_hash=split_hash,  # Conflicting hash
                vote_signature=BftConsensusEngine.sign_vote("agent_llama_31", split_hash, "VOTE_APPROVE"),
            ),
        ]

        cert = self.engine.execute_consensus_round("PROP-ALPHA-01", self.sample_proposal, injected_votes=votes)
        # Approvals for target_hash = 2 < Quorum (3) => Must Reject
        self.assertFalse(cert.consensus_reached)
        self.assertEqual(cert.state, "STATE_REJECTED")
        self.assertEqual(cert.byzantine_faults_count, 2)


if __name__ == "__main__":
    unittest.main()
