"""
Service de gestion des profils utilisateur avec isolation par session
"""
import uuid
from typing import Dict, Optional
from app.models.profile import Profile

# Stockage global des profils par session
# Structure: {session_id: {profile_id: Profile}}
profiles_by_session: Dict[str, Dict[str, Profile]] = {}

class ProfileService:
    """Service pour gérer les profils utilisateur avec isolation par session"""
    
    def get_session_profiles(self, session_id: str) -> Dict[str, Profile]:
        """
        Récupère tous les profils d'une session
        
        Args:
            session_id: Identifiant de session
            
        Returns:
            Dictionnaire des profils de la session
        """
        return profiles_by_session.get(session_id, {})
    
    def save_profile(self, session_id: str, profile_id: str, profile: Profile) -> None:
        """
        Sauvegarde un profil dans une session
        
        Args:
            session_id: Identifiant de session
            profile_id: Identifiant unique du profil
            profile: Profil à sauvegarder
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"🔄 SAVE_PROFILE - session_id: {session_id}, profile_id: {profile_id}")
        
        if session_id not in profiles_by_session:
            profiles_by_session[session_id] = {}
            logger.info(f"📝 Created new session storage for: {session_id}")
        
        profiles_by_session[session_id][profile_id] = profile
        
        # Log current state
        logger.info(f"✅ Profile saved successfully")
        logger.info(f"📊 Total sessions: {len(profiles_by_session)}")
        logger.info(f"📊 Profiles in this session: {len(profiles_by_session[session_id])}")
        logger.debug(f"🗂️ All session IDs: {list(profiles_by_session.keys())}")
        logger.debug(f"🗂️ Profile IDs in session {session_id}: {list(profiles_by_session[session_id].keys())}")
    
    def get_profile(self, session_id: str, profile_id: str) -> Optional[Profile]:
        """
        Récupère un profil spécifique d'une session
        
        Args:
            session_id: Identifiant de session
            profile_id: Identifiant du profil
            
        Returns:
            Le profil s'il existe, None sinon
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"🔍 GET_PROFILE - session_id: {session_id}, profile_id: {profile_id}")
        
        # Log current storage state
        logger.info(f"📊 Total sessions in storage: {len(profiles_by_session)}")
        logger.debug(f"🗂️ All session IDs in storage: {list(profiles_by_session.keys())}")
        
        # Check if session exists
        if session_id not in profiles_by_session:
            logger.warning(f"❌ Session {session_id} not found in storage")
            logger.debug(f"🔍 Available sessions: {list(profiles_by_session.keys())}")
            return None
        
        session_profiles = profiles_by_session.get(session_id, {})
        logger.info(f"📊 Profiles in session {session_id}: {len(session_profiles)}")
        logger.debug(f"🗂️ Profile IDs in session: {list(session_profiles.keys())}")
        
        # Check if profile exists in session
        if profile_id not in session_profiles:
            logger.warning(f"❌ Profile {profile_id} not found in session {session_id}")
            logger.debug(f"🔍 Available profiles in session: {list(session_profiles.keys())}")
            return None
        
        profile = session_profiles.get(profile_id)
        if profile:
            logger.info(f"✅ Profile {profile_id} found and returned")
        else:
            logger.error(f"❌ Profile {profile_id} exists in dict but is None/empty")
        
        return profile
    
    def delete_profile(self, session_id: str, profile_id: str) -> bool:
        """
        Supprime un profil d'une session
        
        Args:
            session_id: Identifiant de session
            profile_id: Identifiant du profil
            
        Returns:
            True si le profil a été supprimé, False s'il n'existait pas
        """
        session_profiles = profiles_by_session.get(session_id, {})
        if profile_id in session_profiles:
            del session_profiles[profile_id]
            return True
        return False
    
    def generate_profile_id(self) -> str:
        """
        Génère un identifiant unique pour un profil
        
        Returns:
            UUID sous forme de string
        """
        return str(uuid.uuid4())
    
    def get_session_count(self) -> int:
        """
        Retourne le nombre de sessions actives (pour debug)
        
        Returns:
            Nombre de sessions
        """
        return len(profiles_by_session)
    
    def get_total_profiles_count(self) -> int:
        """
        Retourne le nombre total de profils (pour debug)
        
        Returns:
            Nombre total de profils
        """
        return sum(len(profiles) for profiles in profiles_by_session.values())
