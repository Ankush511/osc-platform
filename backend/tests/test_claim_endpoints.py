"""
Tests for claim management API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.main import app
from app.api.dependencies import get_db
from app.models.issue import Issue, IssueStatus


@pytest.fixture
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestClaimIssueEndpoint:
    """Tests for POST /api/v1/issues/{issue_id}/claim"""
    
    def test_claim_issue_success(self, client, sample_issue, test_user):
        """Test successfully claiming an issue via API"""
        response = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": test_user.id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["issue_id"] == sample_issue.id
        assert "claimed_at" in data
        assert "claim_expires_at" in data
    
    def test_claim_already_claimed_issue(self, client, sample_issue, test_user, second_user):
        """Test claiming an already claimed issue returns 400"""
        # First user claims
        response1 = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": test_user.id}
        )
        assert response1.status_code == 200
        
        # Second user tries to claim
        response2 = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": second_user.id}
        )
        assert response2.status_code == 400
        assert "already claimed" in response2.json()["detail"].lower()
    
    def test_claim_nonexistent_issue(self, client, test_user):
        """Test claiming non-existent issue returns 400"""
        response = client.post(
            "/api/v1/issues/99999/claim",
            json={"user_id": test_user.id}
        )
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
    
    def test_claim_issue_invalid_request(self, client, sample_issue):
        """Test claiming with invalid request body"""
        response = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={}
        )
        
        assert response.status_code == 422  # Validation error


class TestReleaseIssueEndpoint:
    """Tests for POST /api/v1/issues/{issue_id}/release"""
    
    def test_release_issue_success(self, client, sample_issue, test_user):
        """Test successfully releasing an issue via API"""
        # First claim the issue
        claim_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": test_user.id}
        )
        assert claim_response.status_code == 200
        
        # Then release it
        release_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/release",
            json={"user_id": test_user.id}
        )
        
        assert release_response.status_code == 200
        data = release_response.json()
        assert data["success"] is True
        assert data["issue_id"] == sample_issue.id
    
    def test_release_unclaimed_issue(self, client, sample_issue, test_user):
        """Test releasing an unclaimed issue returns 400"""
        response = client.post(
            f"/api/v1/issues/{sample_issue.id}/release",
            json={"user_id": test_user.id}
        )
        
        assert response.status_code == 400
        assert "not claimed" in response.json()["detail"].lower()
    
    def test_release_issue_claimed_by_another_user(self, client, sample_issue, test_user, second_user):
        """Test releasing issue claimed by another user returns 400"""
        # First user claims
        claim_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": test_user.id}
        )
        assert claim_response.status_code == 200
        
        # Second user tries to release
        release_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/release",
            json={"user_id": second_user.id}
        )
        
        assert release_response.status_code == 400
        assert "only release" in release_response.json()["detail"].lower()


class TestExtendClaimDeadlineEndpoint:
    """Tests for POST /api/v1/issues/{issue_id}/extend"""
    
    def test_extend_deadline_success(self, client, sample_issue, test_user):
        """Test successfully extending deadline via API"""
        # First claim the issue
        claim_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": test_user.id}
        )
        assert claim_response.status_code == 200
        
        # Extend the deadline
        extend_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/extend",
            json={
                "user_id": test_user.id,
                "justification": "Need more time to complete comprehensive testing",
                "extension_days": 7
            }
        )
        
        assert extend_response.status_code == 200
        data = extend_response.json()
        assert data["success"] is True
        assert data["issue_id"] == sample_issue.id
        assert "new_expiration" in data
    
    def test_extend_deadline_custom_days(self, client, sample_issue, test_user):
        """Test extending deadline with custom number of days"""
        # Claim the issue
        claim_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": test_user.id}
        )
        assert claim_response.status_code == 200
        
        # Extend by 14 days
        extend_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/extend",
            json={
                "user_id": test_user.id,
                "justification": "Complex issue requires significant refactoring",
                "extension_days": 14
            }
        )
        
        assert extend_response.status_code == 200
        data = extend_response.json()
        assert data["success"] is True
    
    def test_extend_unclaimed_issue(self, client, sample_issue, test_user):
        """Test extending unclaimed issue returns 400"""
        response = client.post(
            f"/api/v1/issues/{sample_issue.id}/extend",
            json={
                "user_id": test_user.id,
                "justification": "Test justification",
                "extension_days": 7
            }
        )
        
        assert response.status_code == 400
        assert "not claimed" in response.json()["detail"].lower()
    
    def test_extend_issue_claimed_by_another_user(self, client, sample_issue, test_user, second_user):
        """Test extending issue claimed by another user returns 400"""
        # First user claims
        claim_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": test_user.id}
        )
        assert claim_response.status_code == 200
        
        # Second user tries to extend
        extend_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/extend",
            json={
                "user_id": second_user.id,
                "justification": "Test justification",
                "extension_days": 7
            }
        )
        
        assert extend_response.status_code == 400
        assert "only extend" in extend_response.json()["detail"].lower()
    
    def test_extend_deadline_invalid_justification(self, client, sample_issue, test_user):
        """Test extending with too short justification"""
        # Claim the issue
        claim_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": test_user.id}
        )
        assert claim_response.status_code == 200
        
        # Try to extend with short justification
        extend_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/extend",
            json={
                "user_id": test_user.id,
                "justification": "Short",  # Less than 10 characters
                "extension_days": 7
            }
        )
        
        assert extend_response.status_code == 422  # Validation error


class TestAutoReleaseEndpoint:
    """Tests for POST /api/v1/issues/claims/auto-release"""
    
    def test_auto_release_endpoint(self, client, db_session, sample_issue, test_user):
        """Test auto-release endpoint"""
        # Claim and expire the issue
        claim_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": test_user.id}
        )
        assert claim_response.status_code == 200
        
        # Manually expire the claim
        sample_issue.claim_expires_at = datetime.utcnow() - timedelta(hours=1)
        db_session.commit()
        
        # Trigger auto-release
        response = client.post("/api/v1/issues/claims/auto-release")
        
        assert response.status_code == 200
        data = response.json()
        assert data["released_count"] == 1
        assert sample_issue.id in data["issue_ids"]
    
    def test_auto_release_no_expired_claims(self, client):
        """Test auto-release with no expired claims"""
        response = client.post("/api/v1/issues/claims/auto-release")
        
        assert response.status_code == 200
        data = response.json()
        assert data["released_count"] == 0
        assert len(data["issue_ids"]) == 0


class TestGetExpiringClaimsEndpoint:
    """Tests for GET /api/v1/issues/claims/expiring"""
    
    def test_get_expiring_claims(self, client, db_session, sample_issue, test_user):
        """Test getting expiring claims via API"""
        # Claim the issue
        claim_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": test_user.id}
        )
        assert claim_response.status_code == 200
        
        # Set expiration to 12 hours from now
        sample_issue.claim_expires_at = datetime.utcnow() + timedelta(hours=12)
        db_session.commit()
        
        # Get expiring claims
        response = client.get("/api/v1/issues/claims/expiring?hours=24")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["issues"]) == 1
        assert data["issues"][0]["id"] == sample_issue.id
    
    def test_get_expiring_claims_custom_threshold(self, client, db_session, sample_issue, test_user):
        """Test getting expiring claims with custom threshold"""
        # Claim the issue
        claim_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": test_user.id}
        )
        assert claim_response.status_code == 200
        
        # Set expiration to 10 hours from now
        sample_issue.claim_expires_at = datetime.utcnow() + timedelta(hours=10)
        db_session.commit()
        
        # Should not be found with 6-hour threshold
        response_6h = client.get("/api/v1/issues/claims/expiring?hours=6")
        assert response_6h.status_code == 200
        assert response_6h.json()["count"] == 0
        
        # Should be found with 12-hour threshold
        response_12h = client.get("/api/v1/issues/claims/expiring?hours=12")
        assert response_12h.status_code == 200
        assert response_12h.json()["count"] == 1
    
    def test_get_expiring_claims_empty(self, client):
        """Test getting expiring claims when there are none"""
        response = client.get("/api/v1/issues/claims/expiring")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert len(data["issues"]) == 0


class TestClaimWorkflow:
    """Integration tests for complete claim workflows"""
    
    def test_complete_claim_workflow(self, client, sample_issue, test_user):
        """Test complete workflow: claim -> extend -> release"""
        # 1. Claim the issue
        claim_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": test_user.id}
        )
        assert claim_response.status_code == 200
        claim_data = claim_response.json()
        assert claim_data["success"] is True
        
        # 2. Extend the deadline
        extend_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/extend",
            json={
                "user_id": test_user.id,
                "justification": "Need additional time for thorough testing",
                "extension_days": 7
            }
        )
        assert extend_response.status_code == 200
        extend_data = extend_response.json()
        assert extend_data["success"] is True
        
        # 3. Release the issue
        release_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/release",
            json={"user_id": test_user.id}
        )
        assert release_response.status_code == 200
        release_data = release_response.json()
        assert release_data["success"] is True
        
        # 4. Verify issue is available again
        issue_response = client.get(f"/api/v1/issues/{sample_issue.id}")
        assert issue_response.status_code == 200
        issue_data = issue_response.json()
        assert issue_data["status"] == "available"
        assert issue_data["claimed_by"] is None
    
    def test_claim_transfer_workflow(self, client, sample_issue, test_user, second_user):
        """Test workflow: user1 claims -> releases -> user2 claims"""
        # User 1 claims
        claim1_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": test_user.id}
        )
        assert claim1_response.status_code == 200
        
        # User 1 releases
        release_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/release",
            json={"user_id": test_user.id}
        )
        assert release_response.status_code == 200
        
        # User 2 claims
        claim2_response = client.post(
            f"/api/v1/issues/{sample_issue.id}/claim",
            json={"user_id": second_user.id}
        )
        assert claim2_response.status_code == 200
        
        # Verify user 2 owns it
        issue_response = client.get(f"/api/v1/issues/{sample_issue.id}")
        assert issue_response.status_code == 200
        issue_data = issue_response.json()
        assert issue_data["claimed_by"] == second_user.id
