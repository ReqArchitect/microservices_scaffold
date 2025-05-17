import pytest
from datetime import datetime, timedelta
from app.utils.versioning import APIVersion, VersionManager, api_version

def test_api_version_initialization():
    """Test API version initialization."""
    version = APIVersion('v1')
    assert version.version == 'v1'
    assert version.is_deprecated is False
    assert version.sunset_date is None
    assert version.migration_guide_url is None

def test_api_version_deprecation():
    """Test API version deprecation."""
    version = APIVersion('v1')
    sunset_date = datetime.utcnow() + timedelta(days=30)
    migration_url = 'https://example.com/migration'
    
    version.deprecate(sunset_date, migration_url)
    assert version.is_deprecated is True
    assert version.sunset_date == sunset_date
    assert version.migration_guide_url == migration_url

def test_api_version_decorator():
    """Test API version decorator."""
    version = APIVersion('v1')
    
    @version
    def test_endpoint():
        return {'message': 'success'}
    
    # Test with matching version
    response = test_endpoint(version='v1')
    assert response['message'] == 'success'
    
    # Test with non-matching version
    response = test_endpoint(version='v2')
    assert response.status_code == 404
    assert 'version not found' in response.json['error'].lower()

def test_api_version_deprecated_warning():
    """Test API version deprecation warning."""
    version = APIVersion('v1')
    sunset_date = datetime.utcnow() + timedelta(days=30)
    version.deprecate(sunset_date)
    
    @version
    def test_endpoint():
        return {'message': 'success'}
    
    # Should return success with warning
    response = test_endpoint(version='v1')
    assert response['message'] == 'success'
    assert 'deprecated' in response.headers.get('Warning', '').lower()

def test_api_version_sunset():
    """Test API version sunset."""
    version = APIVersion('v1')
    sunset_date = datetime.utcnow() - timedelta(days=1)  # Past date
    version.deprecate(sunset_date)
    
    @version
    def test_endpoint():
        return {'message': 'success'}
    
    # Should return 410 Gone
    response = test_endpoint(version='v1')
    assert response.status_code == 410
    assert 'sunset' in response.json['error'].lower()

def test_version_manager():
    """Test version manager."""
    manager = VersionManager()
    
    # Register versions
    v1 = manager.register_version('v1')
    v2 = manager.register_version('v2')
    
    assert 'v1' in manager.versions
    assert 'v2' in manager.versions
    assert manager.get_version('v1') == v1
    assert manager.get_version('v2') == v2
    
    # Set current version
    manager.set_current_version('v2')
    assert manager.current_version == 'v2'
    
    # Get all versions
    versions = manager.get_all_versions()
    assert len(versions) == 2
    assert 'v1' in versions
    assert 'v2' in versions

def test_version_manager_invalid_version():
    """Test version manager with invalid version."""
    manager = VersionManager()
    
    # Try to get non-existent version
    with pytest.raises(ValueError):
        manager.get_version('v1')
    
    # Try to set non-existent current version
    with pytest.raises(ValueError):
        manager.set_current_version('v1')

def test_api_version_factory():
    """Test API version factory decorator."""
    @api_version('v1')
    def test_endpoint():
        return {'message': 'success'}
    
    # Test with matching version
    response = test_endpoint(version='v1')
    assert response['message'] == 'success'
    
    # Test with non-matching version
    response = test_endpoint(version='v2')
    assert response.status_code == 404
    assert 'version not found' in response.json['error'].lower()

def test_api_version_factory_deprecated():
    """Test API version factory with deprecated version."""
    sunset_date = datetime.utcnow() + timedelta(days=30)
    
    @api_version('v1', deprecated=True, sunset_date=sunset_date)
    def test_endpoint():
        return {'message': 'success'}
    
    # Should return success with warning
    response = test_endpoint(version='v1')
    assert response['message'] == 'success'
    assert 'deprecated' in response.headers.get('Warning', '').lower() 