import pytest
from app.models import Initiative
from datetime import datetime, timedelta

def test_initiative_creation(app, test_tenant_id, test_user_id):
    """Test initiative creation with valid data."""
    initiative = Initiative(
        title="Test Initiative",
        description="Test Description",
        strategic_objective="Test Objective",
        start_date=datetime.now().date(),
        end_date=(datetime.now() + timedelta(days=30)).date(),
        status="active",
        priority="high",
        progress=50,
        tenant_id=test_tenant_id,
        owner_id=test_user_id,
        created_by=test_user_id,
        updated_by=test_user_id,
        tags="test,example"
    )
    
    assert initiative.title == "Test Initiative"
    assert initiative.status == "active"
    assert initiative.priority == "high"
    assert initiative.progress == 50
    assert initiative.tenant_id == test_tenant_id
    assert initiative.owner_id == test_user_id

def test_initiative_validation_title(app, test_tenant_id, test_user_id):
    """Test initiative title validation."""
    with pytest.raises(ValueError, match="Title cannot be empty"):
        Initiative(
            title="",
            strategic_objective="Test Objective",
            tenant_id=test_tenant_id,
            owner_id=test_user_id,
            created_by=test_user_id,
            updated_by=test_user_id
        )

def test_initiative_validation_strategic_objective(app, test_tenant_id, test_user_id):
    """Test strategic objective validation."""
    with pytest.raises(ValueError, match="Strategic objective cannot be empty"):
        Initiative(
            title="Test Initiative",
            strategic_objective="",
            tenant_id=test_tenant_id,
            owner_id=test_user_id,
            created_by=test_user_id,
            updated_by=test_user_id
        )

def test_initiative_validation_status(app, test_tenant_id, test_user_id):
    """Test status validation."""
    with pytest.raises(ValueError):
        Initiative(
            title="Test Initiative",
            strategic_objective="Test Objective",
            status="invalid_status",
            tenant_id=test_tenant_id,
            owner_id=test_user_id,
            created_by=test_user_id,
            updated_by=test_user_id
        )

def test_initiative_validation_priority(app, test_tenant_id, test_user_id):
    """Test priority validation."""
    with pytest.raises(ValueError):
        Initiative(
            title="Test Initiative",
            strategic_objective="Test Objective",
            priority="invalid_priority",
            tenant_id=test_tenant_id,
            owner_id=test_user_id,
            created_by=test_user_id,
            updated_by=test_user_id
        )

def test_initiative_validation_progress(app, test_tenant_id, test_user_id):
    """Test progress validation."""
    with pytest.raises(ValueError):
        Initiative(
            title="Test Initiative",
            strategic_objective="Test Objective",
            progress=150,  # Invalid progress value
            tenant_id=test_tenant_id,
            owner_id=test_user_id,
            created_by=test_user_id,
            updated_by=test_user_id
        )

def test_initiative_tags_validation(app, test_tenant_id, test_user_id):
    """Test tags validation and normalization."""
    initiative = Initiative(
        title="Test Initiative",
        strategic_objective="Test Objective",
        tags="tag1, tag2, tag1, tag3",  # Duplicate tag
        tenant_id=test_tenant_id,
        owner_id=test_user_id,
        created_by=test_user_id,
        updated_by=test_user_id
    )
    
    assert initiative.tags == "tag1,tag2,tag3"  # Duplicates removed

def test_initiative_to_dict(app, test_tenant_id, test_user_id):
    """Test initiative to_dict method."""
    initiative = Initiative(
        title="Test Initiative",
        description="Test Description",
        strategic_objective="Test Objective",
        start_date=datetime.now().date(),
        end_date=(datetime.now() + timedelta(days=30)).date(),
        status="active",
        priority="high",
        progress=50,
        tenant_id=test_tenant_id,
        owner_id=test_user_id,
        created_by=test_user_id,
        updated_by=test_user_id,
        tags="test,example"
    )
    
    data = initiative.to_dict()
    assert data["title"] == "Test Initiative"
    assert data["status"] == "active"
    assert data["priority"] == "high"
    assert data["progress"] == 50
    assert data["tenant_id"] == test_tenant_id
    assert data["owner_id"] == test_user_id
    assert isinstance(data["tags"], list)
    assert "test" in data["tags"]
    assert "example" in data["tags"] 