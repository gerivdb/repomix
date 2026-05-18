# RESTAdapter - Enrobage ternaire pour APIs REST
# Intégration sécurisée et supervisée des APIs externes

import time
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import threading

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

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


class HTTPMethod(Enum):
    """Méthodes HTTP supportées"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class RESTAdapterConfig:
    """Configuration de l'adaptateur REST"""
    base_url: str
    timeout: int = 30
    retries: int = 3
    backoff_factor: float = 0.3
    headers: Dict[str, str] = None
    # Sécurité Diamond
    require_auth: bool = True
    required_permission: str = "READ"
    # Supervision
    enable_telemetry: bool = True
    # Validation
    validate_response: bool = True
    expected_content_type: str = "application/json"


class RESTAdapter:
    """
    RESTAdapter - Enrobage ternaire pour APIs REST
    Fournit une interface unifiée et sécurisée pour les APIs externes
    avec intégration Diamond (TelemetryVerse, AuthVerse, SecurityGuard)
    """

    def __init__(self, config: RESTAdapterConfig):
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests is required for RESTAdapter. Install with: pip install requests")

        self.config = config
        self._session: Optional[requests.Session] = None
        self._security_guard = SecurityGuard() if SecurityGuard else None
        self._request_count = 0
        self._error_count = 0
        self._lock = threading.Lock()

        # Initialiser la session
        self._initialize_session()

        # Enregistrement dans TelemetryVerse
        if DIAMOND_INTEGRATION and self.config.enable_telemetry:
            telemetry_verse.record_inter_verse_flow("AdapterVerse", "TelemetryVerse", 1024)

    def _initialize_session(self):
        """Initialise la session requests avec retry et configuration"""
        self._session = requests.Session()

        # Configuration des retries
        retry_strategy = Retry(
            total=self.config.retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        # Headers par défaut
        default_headers = {
            "User-Agent": "Diamond-NEXUS-AdapterVerse/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        if self.config.headers:
            default_headers.update(self.config.headers)

        self._session.headers.update(default_headers)

        logger.info(f"RESTAdapter initialized for {self.config.base_url}")

    def _check_authorization(self, user: str, method: HTTPMethod) -> AuthSignature:
        """
        Vérifie l'autorisation via AuthVerse

        Args:
            user: Utilisateur demandant l'accès
            method: Méthode HTTP

        Returns:
            Signature ternaire d'autorisation
        """
        if not self.config.require_auth or not auth_verse:
            return AuthSignature.VALIDE

        # Mapper la méthode HTTP vers une permission
        permission_map = {
            HTTPMethod.GET: "READ",
            HTTPMethod.POST: "WRITE",
            HTTPMethod.PUT: "WRITE",
            HTTPMethod.DELETE: "DELETE",
            HTTPMethod.PATCH: "WRITE",
            HTTPMethod.HEAD: "READ",
            HTTPMethod.OPTIONS: "READ"
        }

        permission = permission_map.get(method, "READ")
        
        # Vérifier via AuthVerse
        return auth_verse.authenticate_verse_access(
            verse_name="AdapterVerse",
            requester=user,
            action=permission,
            context={
                "method": method.value,
                "base_url": self.config.base_url,
                "timestamp": time.time()
            }
        )

    def _record_metrics(self, method: HTTPMethod, url: str, execution_time: float, 
                       status_code: int, success: bool, response_size: int = 0):
        """
        Enregistre les métriques dans TelemetryVerse

        Args:
            method: Méthode HTTP utilisée
            url: URL appelée
            execution_time: Temps d'exécution en secondes
            status_code: Code de statut HTTP
            success: Succès de la requête
            response_size: Taille de la réponse en octets
        """
        if not DIAMOND_INTEGRATION or not self.config.enable_telemetry:
            return

        try:
            # Enregistrer les performances
            telemetry_verse.performance_telemetry.record_metric(
                f"adapter_rest_{method.value.lower()}_time",
                execution_time,
                "seconds",
                {
                    "method": method.value,
                    "url": url,
                    "status_code": status_code,
                    "success": success,
                    "response_size": response_size,
                    "adapter": "RESTAdapter"
                }
            )

            # Enregistrer le flux inter-Verses
            telemetry_verse.record_inter_verse_flow("AdapterVerse", "TelemetryVerse", 512)

            # Enregistrement des erreurs
            if not success or status_code >= 400:
                self._error_count += 1
                telemetry_verse.alert_telemetry.create_alert(
                    AlertSeverity.WARNING if status_code < 500 else AlertSeverity.ERROR,
                    f"REST call {method.value} {url} failed with {status_code}",
                    "RESTAdapter",
                    {
                        "method": method.value,
                        "url": url,
                        "status_code": status_code,
                        "execution_time": execution_time,
                        "success": success
                    }
                )
        except Exception as e:
            logger.warning(f"Failed to record metrics: {e}")

    def _validate_response(self, response: requests.Response) -> AuthSignature:
        """
        Valide la réponse HTTP selon les invariants

        Args:
            response: Réponse HTTP à valider

        Returns:
            Signature ternaire de validation
        """
        if not self.config.validate_response:
            return AuthSignature.VALIDE

        try:
            # Vérifier le content-type si spécifié
            if self.config.expected_content_type:
                content_type = response.headers.get('content-type', '').split(';')[0].strip()
                if content_type != self.config.expected_content_type:
                    logger.warning(f"Unexpected content-type: {content_type}, expected: {self.config.expected_content_type}")

            # Pour les réponses JSON, vérifier que c'est du JSON valide
            if self.config.expected_content_type == "application/json":
                try:
                    response.json()
                except json.JSONDecodeError:
                    return AuthSignature.INVALIDE

            # Vérifier les codes de statut
            if 200 <= response.status_code < 300:
                return AuthSignature.VALIDE
            elif 300 <= response.status_code < 400:
                return AuthSignature.NEUTRE  # Redirections
            else:
                return AuthSignature.INVALIDE

        except Exception as e:
            logger.error(f"Response validation error: {e}")
            return AuthSignature.INVALIDE

    def _make_request(self, method: HTTPMethod, endpoint: str, 
                     params: Dict = None, data: Any = None, json_data: Any = None,
                     headers: Dict = None, user: str = "system") -> Dict[str, Any]:
        """
        Méthode interne pour effectuer les requêtes HTTP

        Args:
            method: Méthode HTTP
            endpoint: Endpoint relatif à base_url
            params: Paramètres de requête
            data: Données brutes
            json_data: Données JSON
            headers: Headers supplémentaires
            user: Utilisateur effectuant la requête

        Returns:
            Résultat de la requête avec métadonnées
        """
        start_time = time.time()
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        try:
            # Vérification d'autorisation
            auth_signature = self._check_authorization(user, method)
            if auth_signature == AuthSignature.INVALIDE:
                raise PermissionError(f"Access denied for user {user} to execute {method.value}")

            # Préparation de la requête
            request_kwargs = {
                'params': params,
                'timeout': self.config.timeout
            }

            if json_data is not None:
                request_kwargs['json'] = json_data
            elif data is not None:
                request_kwargs['data'] = data if isinstance(data, str) else json.dumps(data)

            if headers:
                request_kwargs['headers'] = {**self._session.headers, **headers}

            # Exécution de la requête
            response = self._session.request(method.value, url, **request_kwargs)
            
            execution_time = time.time() - start_time
            response_size = len(response.content) if response.content else 0

            # Validation de la réponse
            validation_signature = self._validate_response(response)

            # Enregistrement des métriques
            self._record_metrics(method, url, execution_time, response.status_code, 
                               response.status_code < 400, response_size)

            # Mettre à jour les compteurs
            with self._lock:
                self._request_count += 1

            # Préparation de la réponse
            result = {
                "url": url,
                "method": method.value,
                "status_code": response.status_code,
                "execution_time": execution_time,
                "response_size": response_size,
                "auth_signature": auth_signature.value,
                "validation_signature": validation_signature.value,
                "success": response.status_code < 400
            }

            # Gestion du contenu de la réponse
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    result["data"] = response.json()
                else:
                    result["data"] = response.text
            except Exception as e:
                result["data"] = response.text
                result["parse_error"] = str(e)

            # Headers de réponse
            result["response_headers"] = dict(response.headers)

            return result

        except requests.exceptions.RequestException as e:
            execution_time = time.time() - start_time
            logger.error(f"HTTP request failed: {e}")

            # Enregistrement des métriques d'erreur
            self._record_metrics(method, url, execution_time, 0, False)

            return {
                "url": url,
                "method": method.value,
                "status_code": 0,
                "execution_time": execution_time,
                "response_size": 0,
                "auth_signature": AuthSignature.INVALIDE.value,
                "validation_signature": AuthSignature.INVALIDE.value,
                "success": False,
                "error": str(e),
                "data": None
            }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Unexpected error in REST request: {e}")

            return {
                "url": url,
                "method": method.value,
                "status_code": 0,
                "execution_time": execution_time,
                "response_size": 0,
                "auth_signature": AuthSignature.INVALIDE.value,
                "validation_signature": AuthSignature.INVALIDE.value,
                "success": False,
                "error": str(e),
                "data": None
            }

    def get(self, endpoint: str, params: Dict = None, headers: Dict = None, 
            user: str = "system") -> Dict[str, Any]:
        """
        Effectue une requête GET

        Args:
            endpoint: Endpoint relatif à base_url
            params: Paramètres de requête
            headers: Headers supplémentaires
            user: Utilisateur effectuant la requête

        Returns:
            Résultat de la requête GET
        """
        return self._make_request(HTTPMethod.GET, endpoint, params=params, 
                                headers=headers, user=user)

    def post(self, endpoint: str, data: Any = None, json_data: Any = None, 
             headers: Dict = None, user: str = "system") -> Dict[str, Any]:
        """
        Effectue une requête POST

        Args:
            endpoint: Endpoint relatif à base_url
            data: Données brutes
            json_data: Données JSON
            headers: Headers supplémentaires
            user: Utilisateur effectuant la requête

        Returns:
            Résultat de la requête POST
        """
        return self._make_request(HTTPMethod.POST, endpoint, data=data, 
                                json_data=json_data, headers=headers, user=user)

    def put(self, endpoint: str, data: Any = None, json_data: Any = None, 
            headers: Dict = None, user: str = "system") -> Dict[str, Any]:
        """
        Effectue une requête PUT

        Args:
            endpoint: Endpoint relatif à base_url
            data: Données brutes
            json_data: Données JSON
            headers: Headers supplémentaires
            user: Utilisateur effectuant la requête

        Returns:
            Résultat de la requête PUT
        """
        return self._make_request(HTTPMethod.PUT, endpoint, data=data, 
                                json_data=json_data, headers=headers, user=user)

    def delete(self, endpoint: str, headers: Dict = None, 
               user: str = "system") -> Dict[str, Any]:
        """
        Effectue une requête DELETE

        Args:
            endpoint: Endpoint relatif à base_url
            headers: Headers supplémentaires
            user: Utilisateur effectuant la requête

        Returns:
            Résultat de la requête DELETE
        """
        return self._make_request(HTTPMethod.DELETE, endpoint, headers=headers, user=user)

    def patch(self, endpoint: str, data: Any = None, json_data: Any = None, 
              headers: Dict = None, user: str = "system") -> Dict[str, Any]:
        """
        Effectue une requête PATCH

        Args:
            endpoint: Endpoint relatif à base_url
            data: Données brutes
            json_data: Données JSON
            headers: Headers supplémentaires
            user: Utilisateur effectuant la requête

        Returns:
            Résultat de la requête PATCH
        """
        return self._make_request(HTTPMethod.PATCH, endpoint, data=data, 
                                json_data=json_data, headers=headers, user=user)

    def get_connection_info(self) -> Dict[str, Any]:
        """Retourne des informations sur la connexion"""
        return {
            "base_url": self.config.base_url,
            "timeout": self.config.timeout,
            "retries": self.config.retries,
            "backoff_factor": self.config.backoff_factor,
            "default_headers": dict(self._session.headers) if self._session else {},
            "total_requests": self._request_count,
            "total_errors": self._error_count,
            "diamond_integration": DIAMOND_INTEGRATION
        }

    def health_check(self) -> Dict[str, Any]:
        """Effectue un contrôle de santé de la connexion"""
        start_time = time.time()
        try:
            # Tenter un GET simple sur la racine
            response = self._session.get(f"{self.config.base_url.rstrip('/')}/", 
                                       timeout=10)
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if response.status_code < 400 else "degraded",
                "response_time": response_time,
                "status_code": response.status_code,
                "timestamp": time.time(),
                "base_url": self.config.base_url
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": time.time() - start_time,
                "timestamp": time.time(),
                "base_url": self.config.base_url
            }

    def close(self):
        """Ferme la session et nettoie les ressources"""
        if self._session:
            self._session.close()
            logger.info("RESTAdapter session closed")


# Instance globale pour faciliter l'accès (à configurer selon les besoins)
# rest_adapter = None  # À initialiser avec une configuration spécifique