# technology_layer_service

This service models infrastructure and platform layer components for the SaaS platform.

## Domain Models
- Node
- Device
- SystemSoftware
- TechnologyService
- TechnologyInterface
- TechnologyFunction
- TechnologyProcess
- TechnologyInteraction
- TechnologyCollaboration
- Artifact
- Equipment
- Material
- Facility
- CommunicationPath
- DistributionNetwork

## Endpoints
- CRUD for each domain model

## Event-based Communication
- Emits and consumes events for cross-service workflows.

## Auth, Logging, Observability
- Uses common_utils for JWT, logging, error handling, and metrics. 