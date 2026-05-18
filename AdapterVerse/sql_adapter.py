# SQLAdapter - Enrobage ternaire de SQLAlchemy
# Intégration sécurisée et supervisée des bases de données relationnelles

import time
import logging
from typing import Dict, List, Optional, Any, Union
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
import threading

try:
    from sqlalchemy import create_engine, Engine, text, exc
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.pool import QueuePool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Import des composants Diamond
try:
    from ..telemetry_verse import telemetry_verse
    from ..auth_verse import AuthSignature, auth_verse
    from ..security_guard import SecurityGuard, SecurityLevel
    DIAMOND_INTEGRATION = True
except ImportError:
    # Fallback pour les tests indépendants
    DIAMOND_INTEGRATION = False
    # Définitions de secours
    class AuthSignature(Enum):
        VALIDE = "VALIDE"
        NEUTRE = "NEUTRE"
        INVALIDE = "INVALIDE"
    
    class MockTelemetryVerse:
        def record_performance(self, *args, **kwargs): pass
        def record_flow(self, *args, **kwargs): pass
    
    telemetry_verse = MockTelemetryVerse()
    auth_verse = None
    SecurityGuard = None
    SecurityLevel = None

logger = logging.getLogger(__name__)


class DatabaseOperation(Enum):
    """Types d'opérations de base de données"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"


@dataclass
class SQLAdapterConfig:
    """Configuration de l'adaptateur SQL"""
    database_url: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 1800
    echo: bool = False
    # Sécurité Diamond
    require_auth: bool = True
    required_permission: str = "READ"
    # Supervision
    enable_telemetry: bool = True
    # Validation
    validate_invariants: bool = True


class SQLAdapter:
    """
    SQLAdapter - Enrobage ternaire de SQLAlchemy
    Fournit une interface unifiée et sécurisée pour les bases de données relationnelles
    avec intégration Diamond (TelemetryVerse, AuthVerse, SecurityGuard)
    """

    def __init__(self, config: SQLAdapterConfig):
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy is required for SQLAdapter. Install with: pip install sqlalchemy")

        self.config = config
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._security_guard = SecurityGuard() if SecurityGuard else None
        self._connection_count = 0
        self._query_count = 0
        self._error_count = 0
        self._lock = threading.Lock()

        # Initialiser le moteur
        self._initialize_engine()

        # Enregistrement dans TelemetryVerse
        if DIAMOND_INTEGRATION and self.config.enable_telemetry:
            telemetry_verse.record_inter_verse_flow("AdapterVerse", "TelemetryVerse", 1024)

    def _initialize_engine(self):
        """Initialise le moteur SQLAlchemy"""
        try:
            self._engine = create_engine(
                self.config.database_url,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                echo=self.config.echo
            )
            self._session_factory = sessionmaker(bind=self._engine)
            logger.info(f"SQLAdapter initialized for {self.config.database_url}")
        except Exception as e:
            logger.error(f"Failed to initialize SQLAdapter: {e}")
            raise

    @contextmanager
    def _get_session(self):
        """Context manager pour obtenir une session de base de données"""
        if not self._session_factory:
            raise RuntimeError("SQLAdapter not properly initialized")

        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _check_authorization(self, user: str, operation: DatabaseOperation) -> AuthSignature:
        """
        Vérifie l'autorisation via AuthVerse

        Args:
            user: Utilisateur demandant l'accès
            operation: Opération de base de données

        Returns:
            Signature ternaire d'autorisation
        """
        if not self.config.require_auth or not auth_verse:
            return AuthSignature.VALIDE

        # Mapper l'opération vers une permission
        permission_map = {
            DatabaseOperation.SELECT: "READ",
            DatabaseOperation.INSERT: "WRITE",
            DatabaseOperation.UPDATE: "WRITE",
            DatabaseOperation.DELETE: "DELETE",
            DatabaseOperation.CREATE: "ADMIN",
            DatabaseOperation.DROP: "ADMIN",
            DatabaseOperation.ALTER: "ADMIN"
        }

        permission = permission_map.get(operation, "READ")
        
        # Vérifier via AuthVerse
        return auth_verse.authenticate_verse_access(
            verse_name="AdapterVerse",
            requester=user,
            action=permission,
            context={
                "operation": operation.value,
                "database_url": self.config.database_url,
                "timestamp": time.time()
            }
        )

    def _record_metrics(self, operation: DatabaseOperation, execution_time: float, 
                       success: bool, rows_affected: int = 0):
        """
        Enregistre les métriques dans TelemetryVerse

        Args:
            operation: Opération effectuée
            execution_time: Temps d'exécution en secondes
            success: Succès de l'opération
            rows_affected: Nombre de lignes affectées
        """
        if not DIAMOND_INTEGRATION or not self.config.enable_telemetry:
            return

        try:
            # Enregistrer les performances
            telemetry_verse.performance_telemetry.record_metric(
                f"adapter_sql_{operation.value.lower()}_time",
                execution_time,
                "seconds",
                {
                    "operation": operation.value,
                    "success": success,
                    "rows_affected": rows_affected,
                    "adapter": "SQLAdapter"
                }
            )

            # Enregistrer le flux inter-Verses
            telemetry_verse.record_inter_verse_flow("AdapterVerse", "TelemetryVerse", 512)

            # Enregistrement des erreurs
            if not success:
                self._error_count += 1
                telemetry_verse.alert_telemetry.create_alert(
                    AlertSeverity.WARNING if success else AlertSeverity.ERROR,
                    f"SQL operation {operation.value} failed",
                    "SQLAdapter",
                    {
                        "operation": operation.value,
                        "execution_time": execution_time,
                        "success": success
                    }
                )
        except Exception as e:
            logger.warning(f"Failed to record metrics: {e}")

    def _validate_invariants(self, operation: DatabaseOperation, success: bool) -> AuthSignature:
        """
        Valide les invariants topologiques après opération

        Args:
            operation: Opération effectuée
            success: Succès de l'opération

        Returns:
            Signature ternaire de validation des invariants
        """
        if not self.config.validate_invariants:
            return AuthSignature.VALIDE

        # Pour simplifier, on considère que l'opération réussit si pas d'exception
        # Dans une implémentation plus poussée, on vérifierait les contraintes de la base
        if success:
            return AuthSignature.VALIDE
        else:
            return AuthSignature.INVALIDE

    def execute_query(self, query: str, parameters: Dict = None, 
                     user: str = "system") -> Dict[str, Any]:
        """
        Exécute une requête SQL SELECT

        Args:
            query: Requête SQL à exécuter
            parameters: Paramètres de la requête (optionnel)
            user: Utilisateur effectuant la requête

        Returns:
            Résultat de la requête avec métadonnées
        """
        start_time = time.time()
        operation = DatabaseOperation.SELECT

        try:
            # Vérification d'autorisation
            auth_signature = self._check_authorization(user, operation)
            if auth_signature == AuthSignature.INVALIDE:
                raise PermissionError(f"Access denied for user {user} to execute {operation.value}")

            # Exécution de la requête
            with self._get_session() as session:
                result = session.execute(text(query), parameters or {})
                rows = result.fetchall()
                
                # Conversion en liste de dictionnaires
                if result.returns_rows:
                    columns = result.keys()
                    data = [dict(zip(columns, row)) for row in rows]
                else:
                    data = []

                rows_affected = len(data)
                execution_time = time.time() - start_time

                # Enregistrement des métriques
                self._record_metrics(operation, execution_time, True, rows_affected)

                # Validation des invariants
                invariant_signature = self._validate_invariants(operation, True)

                # Mettre à jour les compteurs
                with self._lock:
                    self._query_count += 1
                    self._connection_count += 1

                return {
                    "data": data,
                    "row_count": rows_affected,
                    "execution_time": execution_time,
                    "auth_signature": auth_signature.value,
                    "invariant_signature": invariant_signature.value,
                    "operation": operation.value,
                    "success": True
                }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"SQL query execution failed: {e}")

            # Enregistrement des métriques d'erreur
            self._record_metrics(operation, execution_time, False)

            # Validation des invariants en cas d'échec
            invariant_signature = self._validate_invariants(operation, False)

            return {
                "data": [],
                "row_count": 0,
                "execution_time": execution_time,
                "auth_signature": AuthSignature.INVALIDE.value,  # Échec d'autorisation ou autre
                "invariant_signature": invariant_signature.value,
                "operation": operation.value,
                "success": False,
                "error": str(e)
            }

    def execute_command(self, command: str, parameters: Dict = None,
                       user: str = "system") -> Dict[str, Any]:
        """
        Exécute une commande SQL (INSERT, UPDATE, DELETE, etc.)

        Args:
            command: Commande SQL à exécuter
            parameters: Paramètres de la commande (optionnel)
            user: Utilisateur effectuant la commande

        Returns:
 Résultat de la commande avec métadonnées
        """
        start_time = time.time()
        
        # Déterminer le type d'opération
        command_upper = command.strip().upper()
        if command_upper.startswith("INSERT"):
            operation = DatabaseOperation.INSERT
        elif command_upper.startswith("UPDATE"):
            operation = DatabaseOperation.UPDATE
        elif command_upper.startswith("DELETE"):
            operation = DatabaseOperation.DELETE
        elif command_upper.startswith("CREATE"):
            operation = DatabaseOperation.CREATE
        elif command_upper.startswith("DROP"):
            operation = DatabaseOperation.DROP
        elif command_upper.startswith("ALTER"):
            operation = DatabaseOperation.ALTER
        else:
            operation = DatabaseOperation.UPDATE  # Par défaut

        try:
            # Vérification d'autorisation
            auth_signature = self._check_authorization(user, operation)
            if auth_signature == AuthSignature.INVALIDE:
                raise PermissionError(f"Access denied for user {user} to execute {operation.value}")

            # Exécution de la commande
            with self._get_session() as session:
                result = session.execute(text(command), parameters or {})
                rows_affected = result.rowcount
                execution_time = time.time() - start_time

                # Enregistrement des métriques
                self._record_metrics(operation, execution_time, True, rows_affected)

                # Validation des invariants
                invariant_signature = self._validate_invariants(operation, True)

                # Mettre à jour les compteurs
                with self._lock:
                    self._query_count += 1

                return {
                    "row_count": rows_affected,
                    "execution_time": execution_time,
                    "auth_signature": auth_signature.value,
                    "invariant_signature": invariant_signature.value,
                    "operation": operation.value,
                    "success": True
                }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"SQL command execution failed: {e}")

            # Enregistrement des métriques d'erreur
            self._record_metrics(operation, execution_time, False)

            # Validation des invariants en cas d'échec
            invariant_signature = self._validate_invariants(operation, False)

            return {
                "row_count": 0,
                "execution_time": execution_time,
                "auth_signature": AuthSignature.INVALIDE.value,
                "invariant_signature": invariant_signature.value,
                "operation": operation.value,
                "success": False,
                "error": str(e)
            }

    def get_connection_info(self) -> Dict[str, Any]:
        """Retourne des informations sur la connexion"""
        return {
            "database_url": self.config.database_url,
            "pool_size": self.config.pool_size,
            "max_overflow": self.config.max_overflow,
            "echo": self.config.echo,
            "total_queries": self._query_count,
            "total_errors": self._error_count,
            "active_connections": self._connection_count,
            "diamond_integration": DIAMOND_INTEGRATION
        }

    def health_check(self) -> Dict[str, Any]:
        """Effectue un contrôle de santé de la connexion"""
        start_time = time.time()
        try:
            with self._get_session() as session:
                session.execute(text("SELECT 1"))
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "timestamp": time.time(),
                "database_url": self.config.database_url.split("://")[0] + "://[HIDDEN]"  # Masquer les credentials
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": time.time() - start_time,
                "timestamp": time.time(),
                "database_url": self.config.database_url.split("://")[0] + "://[HIDDEN]"
            }

    def close(self):
        """Ferme les connexions et nettoie les ressources"""
        if self._engine:
            self._engine.dispose()
            logger.info("SQLAdapter connections closed")


# Instance globale pour faciliter l'accès (à configurer selon les besoins)
# sql_adapter = None  # À initialiser avec une configuration spécifique