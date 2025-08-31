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
        if session_id not in profiles_by_session:
            profiles_by_session[session_id] = {}
        
        profiles_by_session[session_id][profile_id] = profile
    
    def get_profile(self, session_id: str, profile_id: str) -> Optional[Profile]:
        """
        Récupère un profil spécifique d'une session
        
        Args:
            session_id: Identifiant de session
            profile_id: Identifiant du profil
            
        Returns:
            Le profil s'il existe, None sinon
        """
        session_profiles = profiles_by_session.get(session_id, {})
        return session_profiles.get(profile_id)
    
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
