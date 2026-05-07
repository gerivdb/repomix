import pytest
import asyncio
from datetime import datetime, timedelta
from cli_anything_engine.lifecycle_manager import (
    LifecycleManager, CLIEntity, LifecycleAction
)

class TestLifecycleManager:
    """Tests pour LifecycleManager"""

    @pytest.fixture
    def config(self):
        from cli_anything_engine.config import CLIAnythingConfig
        return CLIAnythingConfig()

    @pytest.fixture
    def manager(self, config):
        return LifecycleManager(config)

    @pytest.mark.asyncio
    async def test_register_entity(self, manager):
        """Test enregistrement entité"""
        entity_data = {
            'id': 'test-entity-001',
            'name': 'TestEntity',
            'version': '1.0.0',
            'dependencies': ['nexus', 'kiva']
        }

        # entity = await manager.register_entity(entity_data)

        assert isinstance(entity, CLIEntity)
        assert entity.id == entity_data['id']
        assert entity.name == entity_data['name']
        assert entity.status == 'active'
        assert entity.usage_count == 0
        assert entity.health_score == 1.0
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.last_updated, datetime)

        # Vérifier stockage
        assert entity.id in manager.entities
        assert manager.entities[entity.id] is entity

    @pytest.mark.asyncio
    async def test_record_usage(self, manager):
        """Test enregistrement utilisation"""
        entity_data = {'id': 'test-usage', 'name': 'TestUsage'}
        # entity = await manager.register_entity(entity_data)

        # Enregistrer utilisation
        await manager.record_usage(entity.id, 5)

        assert manager.entities[entity.id].usage_count == 5
        assert manager.entities[entity.id].last_updated > entity.last_updated

    @pytest.mark.asyncio
    async def test_update_entity_health(self, manager):
        """Test mise à jour health score"""
        entity_data = {'id': 'test-health', 'name': 'TestHealth'}
        # entity = await manager.register_entity(entity_data)

        await manager.update_entity_health(entity.id, 0.8)

        assert manager.entities[entity.id].health_score == 0.8
        assert manager.entities[entity.id].last_updated > entity.last_updated

    @pytest.mark.asyncio
    async def test_run_lifecycle_checks_no_actions(self, manager):
        """Test vérifications lifecycle sans actions"""
        entity_data = {
            'id': 'test-no-action',
            'name': 'TestNoAction',
            'dependencies': []
        }
        # entity = await manager.register_entity(entity_data)

        # Entité récente et saine
        entity.last_updated = datetime.now()
        entity.health_score = 1.0
        entity.usage_count = 100

        actions = await manager.run_lifecycle_checks()

        assert isinstance(actions, list)
        assert len(actions) == 0

    @pytest.mark.asyncio
    async def test_run_lifecycle_checks_update_needed(self, manager):
        """Test vérifications lifecycle avec mise à jour nécessaire"""
        entity_data = {
            'id': 'test-update-needed',
            'name': 'TestUpdateNeeded',
            'dependencies': []
        }
        # entity = await manager.register_entity(entity_data)

        # Simuler entité ancienne
        entity.last_updated = datetime.now() - timedelta(days=100)
        entity.health_score = 0.9
        entity.usage_count = 50

        actions = await manager.run_lifecycle_checks()

        assert isinstance(actions, list)
        assert len(actions) > 0

        # Devrait avoir une action de mise à jour
        update_actions = [a for a in actions if a.action_type == 'update']
        assert len(update_actions) > 0

        action = update_actions[0]
        assert action.entity_id == entity.id
        assert action.priority in ['low', 'medium', 'high', 'critical']
        assert isinstance(action.reason, str)

    @pytest.mark.asyncio
    async def test_run_lifecycle_checks_deprecate_needed(self, manager):
        """Test vérifications lifecycle avec dépréciation nécessaire"""
        entity_data = {
            'id': 'test-deprecate',
            'name': 'TestDeprecate',
            'dependencies': []
        }
        # entity = await manager.register_entity(entity_data)

        # Simuler faible utilisation
        entity.usage_count = 1
        entity.last_updated = datetime.now()

        actions = await manager.run_lifecycle_checks()

        assert isinstance(actions, list)
        # Peut avoir action de dépréciation selon seuils

    @pytest.mark.asyncio
    async def test_execute_update_action(self, manager):
        """Test exécution action de mise à jour"""
        entity_data = {'id': 'test-execute-update', 'name': 'TestExecuteUpdate'}
        # entity = await manager.register_entity(entity_data)

        action = LifecycleAction(
            entity_id=entity.id,
            action_type='update',
            reason='Test update',
            priority='medium',
            scheduled_at=None,
            metadata={'test': True}
        )

        success = await manager._execute_action(action)

        assert success is True

        # Vérifier métriques
        metrics = manager.get_metrics()
        assert metrics['updates_completed'] > 0

    @pytest.mark.asyncio
    async def test_execute_deprecate_action(self, manager):
        """Test exécution action de dépréciation"""
        entity_data = {'id': 'test-execute-deprecate', 'name': 'TestExecuteDeprecate'}
        # entity = await manager.register_entity(entity_data)

        action = LifecycleAction(
            entity_id=entity.id,
            action_type='deprecate',
            reason='Test deprecation',
            priority='low',
            scheduled_at=None,
            metadata={'test': True}
        )

        success = await manager._execute_action(action)

        assert success is True
        assert manager.entities[entity.id].status == 'deprecated'

    @pytest.mark.asyncio
    async def test_execute_archive_action(self, manager):
        """Test exécution action d'archivage"""
        entity_data = {'id': 'test-execute-archive', 'name': 'TestExecuteArchive'}
        # entity = await manager.register_entity(entity_data)

        action = LifecycleAction(
            entity_id=entity.id,
            action_type='archive',
            reason='Test archival',
            priority='low',
            scheduled_at=None,
            metadata={'test': True}
        )

        success = await manager._execute_action(action)

        assert success is True
        assert manager.entities[entity.id].status == 'archived'

        # Vérifier métriques
        metrics = manager.get_metrics()
        assert metrics['archivals_performed'] > 0

    @pytest.mark.asyncio
    async def test_execute_pending_actions(self, manager):
        """Test exécution actions en attente"""
        # Ajouter actions à la queue
        action1 = LifecycleAction(
            entity_id='nonexistent',
            action_type='update',
            reason='Test action 1',
            priority='medium',
            scheduled_at=None,
            metadata={}
        )

        manager.actions_queue.append(action1)

        results = await manager.execute_pending_actions()

        assert isinstance(results, dict)
        assert 'executed' in results
        assert 'failed' in results
        assert 'details' in results

        # Action devrait échouer (entité inexistante)
        assert results['failed'] == 1
        assert results['executed'] == 0
        assert len(manager.actions_queue) == 0  # Retirée même en échec

    def test_prioritize_actions(self, manager):
        """Test priorisation des actions"""
        actions = [
            LifecycleAction('e1', 'update', 'test', 'low', None, {}),
            LifecycleAction('e2', 'archive', 'test', 'high', None, {}),
            LifecycleAction('e3', 'deprecate', 'test', 'critical', None, {}),
            LifecycleAction('e4', 'update', 'test', 'medium', None, {})
        ]

        prioritized = manager._prioritize_actions(actions)

        # Vérifier ordre: critical, high, medium, low
        priorities = [a.priority for a in prioritized]
        assert priorities[0] == 'critical'
        assert priorities[1] == 'high'
        assert priorities[2] == 'medium'
        assert priorities[3] == 'low'

    def test_get_entity_status(self, manager):
        """Test récupération statut entité"""
        entity_data = {'id': 'test-status', 'name': 'TestStatus'}
        # entity = await manager.register_entity(entity_data)

        status = manager.get_entity_status(entity.id)

        assert status is entity
        assert status.status == 'active'

        # Entité inexistante
        status_none = manager.get_entity_status('nonexistent')
        assert status_none is None

    def test_get_metrics(self, manager):
        """Test récupération métriques"""
        metrics = manager.get_metrics()

        expected_keys = [
            'entities_managed',
            'actions_triggered',
            'updates_completed',
            'archivals_performed',
            'active_entities',
            'deprecated_entities',
            'archived_entities',
            'pending_actions'
        ]

        for key in expected_keys:
            assert key in metrics
            assert isinstance(metrics[key], int)
            assert metrics[key] >= 0