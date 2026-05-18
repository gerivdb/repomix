# AdapterVerse - Connecteurs Transverses Externes
# Orchestration des adaptateurs SQL et REST avec enveloppe ternaire Diamond

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Import avec fallback pour les tests indépendants
try:
    from .sql_adapter import SQLAdapter, SQLAdapterConfig, DatabaseOperation
    from .rest_adapter import RESTAdapter, RESTAdapterConfig, HTTPMethod
except ImportError:
    # Fallback pour les tests indépendants
    from sql_adapter import SQLAdapter, SQLAdapterConfig, DatabaseOperation
    from rest_adapter import RESTAdapter, RESTAdapterConfig, HTTPMethod

# Import des composants Diamond
try:
    from ..telemetry_verse import telemetry_verse
    from ..auth_verse import AuthSignature, auth_verse
    DIAMOND_INTEGRATION = True
except ImportError:
    DIAMOND_INTEGRATION = False
    class AuthSignature(Enum):
        VALIDE = "VALIDE"
        NEUTRE = "NEUTRE"
        INVALIDE = "INVALIDE"

logger = logging.getLogger(__name__)


class AdapterType(Enum):
    """Types d'adaptateurs supportés"""
    SQL = "SQL"
    REST = "REST"


@dataclass
class AdapterVerseConfig:
    """Configuration globale d'AdapterVerse"""
    enable_telemetry: bool = True
    enable_auth: bool = True
    enable_security: bool = True
    max_connections_per_adapter: int = 10
    connection_timeout: int = 30


class AdapterVerse:
    """
    AdapterVerse - Connecteurs Transverses Externes
    Orchestration unifiée des adaptateurs SQL et REST avec enveloppe ternaire Diamond
    """

    def __init__(self, config: Optional[AdapterVerseConfig] = None):
        self.config = config or AdapterVerseConfig()
        self._adapters: Dict[str, Any] = {}
        self._active_connections = 0

        # Métriques globales
        self._metrics = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'adapters_created': 0,
            'connections_active': 0
        }

        logger.info("AdapterVerse initialized")

    def create_sql_adapter(self, name: str, config: SQLAdapterConfig) -> SQLAdapter:
        """
        Crée un adaptateur SQL

        Args:
            name: Nom unique de l'adaptateur
            config: Configuration SQL

        Returns:
            Instance de SQLAdapter configurée
        """
        if name in self._adapters:
            raise ValueError(f"Adapter '{name}' already exists")

        adapter = SQLAdapter(config)
        self._adapters[name] = {
            'type': AdapterType.SQL,
            'instance': adapter,
            'config': config
        }

        self._metrics['adapters_created'] += 1

        if DIAMOND_INTEGRATION and self.config.enable_telemetry:
            telemetry_verse.record_inter_verse_flow("AdapterVerse", "TelemetryVerse", 256)

        logger.info(f"SQLAdapter '{name}' created for {config.database_url}")
        return adapter

    def create_rest_adapter(self, name: str, config: RESTAdapterConfig) -> RESTAdapter:
        """
        Crée un adaptateur REST

        Args:
            name: Nom unique de l'adaptateur
            config: Configuration REST

        Returns:
            Instance de RESTAdapter configurée
        """
        if name in self._adapters:
            raise ValueError(f"Adapter '{name}' already exists")

        adapter = RESTAdapter(config)
        self._adapters[name] = {
            'type': AdapterType.REST,
            'instance': adapter,
            'config': config
        }

        self._metrics['adapters_created'] += 1

        if DIAMOND_INTEGRATION and self.config.enable_telemetry:
            telemetry_verse.record_inter_verse_flow("AdapterVerse", "TelemetryVerse", 256)

        logger.info(f"RESTAdapter '{name}' created for {config.base_url}")
        return adapter

    def get_adapter(self, name: str) -> Optional[Any]:
        """
        Récupère un adaptateur par son nom

        Args:
            name: Nom de l'adaptateur

        Returns:
            Instance de l'adaptateur ou None
        """
        adapter_info = self._adapters.get(name)
        return adapter_info['instance'] if adapter_info else None

    def get_sql_adapter(self, name: str) -> Optional[SQLAdapter]:
        """
        Récupère un adaptateur SQL par son nom

        Args:
            name: Nom de l'adaptateur SQL

        Returns:
            Instance de SQLAdapter ou None
        """
        adapter_info = self._adapters.get(name)
        if adapter_info and adapter_info['type'] == AdapterType.SQL:
            return adapter_info['instance']
        return None

    def get_rest_adapter(self, name: str) -> Optional[RESTAdapter]:
        """
        Récupère un adaptateur REST par son nom

        Args:
            name: Nom de l'adaptateur REST

        Returns:
            Instance de RESTAdapter ou None
        """
        adapter_info = self._adapters.get(name)
        if adapter_info and adapter_info['type'] == AdapterType.REST:
            return adapter_info['instance']
        return None

    def remove_adapter(self, name: str) -> bool:
        """
        Supprime un adaptateur

        Args:
            name: Nom de l'adaptateur à supprimer

        Returns:
            True si supprimé avec succès
        """
        if name not in self._adapters:
            return False

        adapter_info = self._adapters[name]
        adapter_instance = adapter_info['instance']

        # Fermer proprement l'adaptateur
        if hasattr(adapter_instance, 'close'):
            adapter_instance.close()

        del self._adapters[name]
        logger.info(f"Adapter '{name}' removed")
        return True

    def list_adapters(self) -> List[Dict[str, Any]]:
        """
        Liste tous les adaptateurs configurés

        Returns:
            Liste des informations sur les adaptateurs
        """
        return [
            {
                'name': name,
                'type': info['type'].value,
                'config': str(info['config'])  # Version simplifiée
            }
            for name, info in self._adapters.items()
        ]

    def execute_sql_query(self, adapter_name: str, query: str, 
                         parameters: Dict = None, user: str = "system") -> Dict[str, Any]:
        """
        Exécute une requête SQL via un adaptateur nommé

        Args:
            adapter_name: Nom de l'adaptateur SQL
            query: Requête SQL
            parameters: Paramètres de la requête
            user: Utilisateur effectuant la requête

        Returns:
            Résultat de la requête
        """
        adapter = self.get_sql_adapter(adapter_name)
        if not adapter:
            return {
                "success": False,
                "error": f"SQL adapter '{adapter_name}' not found",
                "auth_signature": AuthSignature.INVALIDE.value,
                "validation_signature": AuthSignature.INVALIDE.value
            }

        self._metrics['total_operations'] += 1

        result = adapter.execute_query(query, parameters, user)

        if result['success']:
            self._metrics['successful_operations'] += 1
        else:
            self._metrics['failed_operations'] += 1

        return result

    def execute_sql_command(self, adapter_name: str, command: str,
                           parameters: Dict = None, user: str = "system") -> Dict[str, Any]:
        """
        Exécute une commande SQL via un adaptateur nommé

        Args:
            adapter_name: Nom de l'adaptateur SQL
            command: Commande SQL
            parameters: Paramètres de la commande
            user: Utilisateur effectuant la requête

        Returns:
            Résultat de la commande
        """
        adapter = self.get_sql_adapter(adapter_name)
        if not adapter:
            return {
                "success": False,
                "error": f"SQL adapter '{adapter_name}' not found",
                "auth_signature": AuthSignature.INVALIDE.value,
                "validation_signature": AuthSignature.INVALIDE.value
            }

        self._metrics['total_operations'] += 1

        result = adapter.execute_command(command, parameters, user)

        if result['success']:
            self._metrics['successful_operations'] += 1
        else:
            self._metrics['failed_operations'] += 1

        return result

    def call_rest_api(self, adapter_name: str, method: str, endpoint: str,
                     params: Dict = None, data: Any = None, json_data: Any = None,
                     headers: Dict = None, user: str = "system") -> Dict[str, Any]:
        """
        Effectue un appel REST via un adaptateur nommé

        Args:
            adapter_name: Nom de l'adaptateur REST
            method: Méthode HTTP (GET, POST, PUT, DELETE, PATCH)
            endpoint: Endpoint relatif à base_url
            params: Paramètres de requête
            data: Données brutes
            json_data: Données JSON
            headers: Headers supplémentaires
            user: Utilisateur effectuant la requête

        Returns:
            Résultat de l'appel REST
        """
        adapter = self.get_rest_adapter(adapter_name)
        if not adapter:
            return {
                "success": False,
                "error": f"REST adapter '{adapter_name}' not found",
                "auth_signature": AuthSignature.INVALIDE.value,
                "validation_signature": AuthSignature.INVALIDE.value
            }

        self._metrics['total_operations'] += 1

        try:
            http_method = HTTPMethod(method.upper())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid HTTP method: {method}",
                "auth_signature": AuthSignature.INVALIDE.value,
                "validation_signature": AuthSignature.INVALIDE.value
            }

        # Mapper vers la méthode appropriée
        method_map = {
            HTTPMethod.GET: lambda: adapter.get(endpoint, params, headers, user),
            HTTPMethod.POST: lambda: adapter.post(endpoint, data, json_data, headers, user),
            HTTPMethod.PUT: lambda: adapter.put(endpoint, data, json_data, headers, user),
            HTTPMethod.DELETE: lambda: adapter.delete(endpoint, headers, user),
            HTTPMethod.PATCH: lambda: adapter.patch(endpoint, data, json_data, headers, user)
        }

        result = method_map[http_method]()

        if result['success']:
            self._metrics['successful_operations'] += 1
        else:
            self._metrics['failed_operations'] += 1

        return result

    def get_adapter_health(self, name: str) -> Dict[str, Any]:
        """
        Vérifie la santé d'un adaptateur

        Args:
            name: Nom de l'adaptateur

        Returns:
            Statut de santé de l'adaptateur
        """
        adapter_info = self._adapters.get(name)
        if not adapter_info:
            return {
                "status": "not_found",
                "adapter_name": name,
                "error": f"Adapter '{name}' not found"
            }

        adapter = adapter_info['instance']
        if hasattr(adapter, 'health_check'):
            return adapter.health_check()
        else:
            return {
                "status": "unknown",
                "adapter_name": name,
                "error": "Health check not supported"
            }

    def get_verse_status(self) -> Dict[str, Any]:
        """
        Retourne le statut global d'AdapterVerse

        Returns:
            Statut complet du Verse
        """
        adapters_status = []
        for name, info in self._adapters.items():
            health = self.get_adapter_health(name)
            adapters_status.append({
                "name": name,
                "type": info['type'].value,
                "status": health.get("status", "unknown"),
                "url": health.get("base_url") or health.get("database_url", "unknown")
            })

        return {
            "verse_name": "AdapterVerse",
            "adapters_count": len(self._adapters),
            "adapters": adapters_status,
            "metrics": self._metrics.copy(),
            "diamond_integration": DIAMOND_INTEGRATION,
            "config": {
                "enable_telemetry": self.config.enable_telemetry,
                "enable_auth": self.config.enable_auth,
                "enable_security": self.config.enable_security,
                "max_connections_per_adapter": self.config.max_connections_per_adapter,
                "connection_timeout": self.config.connection_timeout
            }
        }

    def close_all_adapters(self):
        """Ferme tous les adaptateurs et nettoie les ressources"""
        for name, info in list(self._adapters.items()):
            try:
                adapter = info['instance']
                if hasattr(adapter, 'close'):
                    adapter.close()
                del self._adapters[name]
            except Exception as e:
                logger.warning(f"Error closing adapter '{name}': {e}")

        logger.info("All adapters closed")


# Instance globale pour faciliter l'accès
adapter_verse = AdapterVerse()