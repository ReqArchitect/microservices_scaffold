"""
Enhanced service registry client for Consul integration with caching support.
"""
import os
import consul
import socket
from flask import Flask, current_app
import logging
import json
from threading import Timer
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ServiceRegistry:
    """Enhanced service registry client for Consul integration"""
    
    def __init__(self, app=None, service_name=None, service_id=None, service_port=None):
        self.app = app
        self.service_name = service_name
        self.service_id = service_id
        self.service_port = service_port
        self.consul_client = None
        self.cache_refresh_timer = None
        self.watching_keys = set()
        
        if app is not None:
            self.init_app(app)
      def init_app(self, app):
        """Initialize the registry with the Flask app"""
        self.app = app
        
        # Get configuration from app
        self.service_name = self.service_name or app.config.get('SERVICE_NAME')
        self.service_id = self.service_id or app.config.get('SERVICE_ID', f"{self.service_name}-{socket.gethostname()}")
        self.service_port = self.service_port or app.config.get('SERVICE_PORT', 5000)
        
        consul_host = app.config.get('CONSUL_HOST', 'consul')
        consul_port = app.config.get('CONSUL_PORT', 8500)
        
        # Initialize Consul client
        self.consul_client = consul.Consul(host=consul_host, port=consul_port)
        
        # Register service on startup if enabled
        if app.config.get('AUTO_REGISTER_SERVICE', True):
            with app.app_context():
                self.register()
                
        # Setup configuration watches
        self._setup_watches(app)
                
        # Deregister on shutdown
        app.teardown_appcontext(self.deregister_on_shutdown)
        
        # Add health check endpoints
        if not app.view_functions.get('health_check'):
            @app.route('/health', methods=['GET'])
            def health_check():
                return {'status': 'healthy'}, 200
                
        if not app.view_functions.get('cache_refresh'):
            @app.route('/cache/refresh', methods=['POST'])
            def cache_refresh():
                self._refresh_cache_config(app)
                return {'status': 'cache refreshed'}, 200
      def register(self):
        """Register the service with Consul"""
        if not self.consul_client:
            logger.warning("Consul client not initialized, skipping registration")
            return False
            
        try:
            # Get the service host (container name in Docker or hostname)
            host = os.environ.get('HOSTNAME', socket.gethostname())
            
            # Prepare service metadata
            meta = {
                'version': self.app.config.get('VERSION', '1.0.0'),
                'environment': self.app.config.get('FLASK_ENV', 'production'),
                'cache_enabled': str(self.app.config.get('CACHE_TYPE') != 'null').lower(),
                'documentation': f"http://{host}:{self.service_port}/docs",
                'metrics': f"http://{host}:{self.service_port}/metrics"
            }
            
            # Register service with enhanced health checks
            self.consul_client.agent.service.register(
                name=self.service_name,
                service_id=self.service_id,
                address=host,
                port=self.service_port,
                meta=meta,
                tags=['reqarchitect', 'flask', self.service_name],
                checks=[
                    {
                        'http': f"http://{host}:{self.service_port}/health",
                        'interval': '10s',
                        'timeout': '5s',
                        'name': 'HTTP Health'
                    },
                    {
                        'http': f"http://{host}:{self.service_port}/metrics",
                        'interval': '30s',
                        'timeout': '5s',
                        'name': 'Metrics Health'
                    }
                ]
            )
            
            # Register configuration in KV store
            config_key = f"reqarchitect/services/{self.service_name}/config"
            config = {
                k: v for k, v in self.app.config.items()
                if isinstance(v, (str, int, float, bool, list, dict))
                and not k.startswith('_')
                and k not in {'SECRET_KEY', 'SECURITY_PASSWORD_SALT'}
            }
            self.consul_client.kv.put(config_key, json.dumps(config))
            
            logger.info(f"Service {self.service_name} registered with Consul at {host}:{self.service_port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service with Consul: {e}")
            return False
    
    def deregister(self):
        """Deregister the service from Consul"""
        if not self.consul_client:
            return False
            
        try:
            self.consul_client.agent.service.deregister(self.service_id)
            logger.info(f"Service {self.service_id} deregistered from Consul")
            return True
        except Exception as e:
            logger.error(f"Failed to deregister service from Consul: {e}")
            return False
    
    def deregister_on_shutdown(self, exception=None):
        """Callback for Flask app context teardown"""
        self.deregister()
      def get_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service details from Consul with enhanced metadata"""
        if not self.consul_client:
            return None
            
        try:
            _, services = self.consul_client.health.service(service_name, passing=True)
            if not services:
                return None
                
            service = services[0]['Service']
            return {
                'id': service['ID'],
                'name': service['Service'],
                'address': service['Address'],
                'port': service['Port'],
                'tags': service['Tags'],
                'meta': service.get('Meta', {}),
                'health': [
                    {
                        'id': check['CheckID'],
                        'name': check['Name'],
                        'status': check['Status'],
                        'output': check['Output']
                    }
                    for check in services[0]['Checks']
                ]
            }
        except Exception as e:
            logger.error(f"Error getting service details: {str(e)}")
            return None
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all registered services"""
        if not self.consul_client:
            return []
            
        try:
            services = []
            index, service_names = self.consul_client.catalog.services()
            
            for name in service_names:
                if service := self.get_service(name):
                    services.append(service)
            return services
        except Exception as e:
            logger.error(f"Error getting all services: {str(e)}")
            return []
    
    def get_service_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service configuration from Consul KV store"""
        try:
            _, data = self.consul_client.kv.get(f"reqarchitect/services/{service_name}/config")
            if data and data['Value']:
                return json.loads(data['Value'].decode('utf-8'))
        except Exception as e:
            logger.error(f"Error getting service config: {str(e)}")
        return None
    
    def update_service_config(self, config: Dict[str, Any]) -> bool:
        """Update service configuration in Consul KV store"""
        try:
            config_key = f"reqarchitect/services/{self.service_name}/config"
            return self.consul_client.kv.put(config_key, json.dumps(config))
        except Exception as e:
            logger.error(f"Error updating service config: {str(e)}")
            return False
            
    def get_cache_endpoints(self) -> Optional[str]:
        """Get Redis cache endpoints from Consul"""
        try:
            _, data = self.consul_client.kv.get("reqarchitect/cache/redis_endpoints")
            if data and data['Value']:
                return data['Value'].decode('utf-8')
        except Exception as e:
            logger.error(f"Error getting cache endpoints: {str(e)}")
        return None
            
        try:
            _, services = self.consul_client.health.service(service_name, passing=True)
            if services:
                service = services[0]['Service']
                return {
                    'id': service['ID'],
                    'name': service['Service'],
                    'address': service['Address'],
                    'port': service['Port']
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get service details from Consul: {e}")
            return None
    
    def get_service_url(self, service_name):
        """Get a service URL from the registry"""
        service = self.get_service(service_name)
        if service:
            return f"http://{service['address']}:{service['port']}"
        logger.warning(f"Service {service_name} not found in registry")
        # Fall back to environment variable with naming convention
        env_var = f"{service_name.upper().replace('-', '_')}_URL"
        return os.environ.get(env_var)
    
    def _setup_watches(self, app):
        """Setup watches for configuration changes"""
        # Watch cache configuration
        self._watch_key('reqarchitect/cache/redis_endpoints', lambda v: self._refresh_cache_config(app, v))
        
        # Watch service-specific configuration
        service_config_key = f"reqarchitect/services/{self.service_name}/config"
        self._watch_key(service_config_key, lambda v: self._update_service_config(app, v))
    
    def _watch_key(self, key: str, callback):
        """Setup a watch for a specific key"""
        if key in self.watching_keys:
            return
            
        self.watching_keys.add(key)
        index = None
        
        def watch_key():
            nonlocal index
            try:
                index, data = self.consul_client.kv.get(
                    key,
                    index=index
                )
                if data and data['Value']:
                    callback(data['Value'].decode('utf-8'))
            except Exception as e:
                logger.error(f"Error watching key {key}: {str(e)}")
            finally:
                # Schedule next check
                Timer(10.0, watch_key).start()
        
        # Start initial watch
        watch_key()
    
    def _refresh_cache_config(self, app, redis_endpoints: str = None):
        """Refresh cache configuration"""
        try:
            if redis_endpoints:
                app.config['CACHE_REDIS_URL'] = f"redis://{redis_endpoints}"
            
            if hasattr(app, 'cache'):
                app.cache.init_app(app)
                logger.info("Cache configuration refreshed")
        except Exception as e:
            logger.error(f"Error refreshing cache config: {str(e)}")
    
    def _update_service_config(self, app, config_json: str):
        """Update service configuration"""
        try:
            config = json.loads(config_json)
            app.config.update(config)
            logger.info("Service configuration updated")
        except Exception as e:
            logger.error(f"Error updating service config: {str(e)}")
    
    def get_service_health(self, service_name: str) -> List[Dict[str, Any]]:
        """Get health status of all instances of a service"""
        try:
            _, checks = self.consul_client.health.service(service_name)
            return [
                {
                    'id': check['Service']['ID'],
                    'status': check['Checks'][-1]['Status'],
                    'output': check['Checks'][-1]['Output'],
                    'address': check['Service']['Address'],
                    'port': check['Service']['Port']
                }
                for check in checks
            ]
        except Exception as e:
            logger.error(f"Error getting service health: {str(e)}")
            return []
    
    def watch_service_health(self, service_name: str, callback):
        """Watch health status changes for a service"""
        self._watch_key(f"reqarchitect/services/{service_name}/health", callback)
