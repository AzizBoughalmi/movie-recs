"""
Utilitaires pour la gestion des sessions
"""
import uuid
import logging
from fastapi import Request, HTTPException

logger = logging.getLogger(__name__)

def get_or_create_session_id(request: Request) -> str:
    """
    Récupère ou crée un identifiant de session
    
    Args:
        request: Requête FastAPI
        
    Returns:
        Identifiant de session
    """
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id
        logger.info(f"🆔 New session created: {session_id}")
    else:
        logger.debug(f"🆔 Existing session: {session_id}")
    return session_id

def get_session_id(request: Request) -> str:
    """
    Récupère l'identifiant de session (doit exister)
    
    Args:
        request: Requête FastAPI
        
    Returns:
        Identifiant de session
        
    Raises:
        HTTPException: Si aucune session n'existe
    """
    session_id = request.session.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="No active session found")
    return session_id
