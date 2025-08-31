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
        logger.info(f"🆔 NEW SESSION CREATED: {session_id}")
        logger.debug(f"🔧 Session data after creation: {dict(request.session)}")
    else:
        logger.info(f"🆔 EXISTING SESSION FOUND: {session_id}")
        logger.debug(f"🔧 Current session data: {dict(request.session)}")
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
    logger.info(f"🔍 GET_SESSION_ID called")
    logger.debug(f"🔧 Current session data: {dict(request.session)}")
    
    session_id = request.session.get("session_id")
    if not session_id:
        logger.error(f"❌ NO SESSION FOUND - session data: {dict(request.session)}")
        raise HTTPException(status_code=400, detail="No active session found")
    
    logger.info(f"🆔 SESSION FOUND: {session_id}")
    return session_id
