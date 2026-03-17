import unittest
from core.database import SessionLocal, Base, engine
from addons.user_manager.controllers.controller import UserController
from addons.user_manager.models.models import User, AuditLog

class TestUserModuleManager(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Configuration globale pour la classe de test"""
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()
        
        # Nettoyage pour éviter les conflits d'emails des tests précédents
        cls.db.query(AuditLog).delete()
        cls.db.query(User).filter(User.username != "AdminTest").delete()
        cls.db.commit()

        # Création de l'admin de référence pour l'audit
        admin = cls.db.query(User).filter(User.username == "AdminTest").first()
        if not admin:
            admin = User(username="AdminTest", email="admin@fearless.cm", role="admin")
            admin.set_password("AdminPass123")
            cls.db.add(admin)
            cls.db.commit()
            cls.db.refresh(admin)
        
        # ON ATTACHE L'ADMIN À LA CLASSE
        cls.admin = admin 
        cls.controller = UserController(cls.db, current_user_id=cls.admin.id)

    def test_01_creation_et_audit(self):
        """Vérifie la création d'un utilisateur et son log d'audit"""
        user_data = {
            "username": "AgentTest",
            "email": "agent@test.cm",
            "password": "password123",
            "role": "agent"
        }
        success, msg = self.controller.create_user(user_data)
        self.assertTrue(success, f"Erreur de création: {msg}")

        # Vérification de l'Audit (Clé du cahier des charges)
        # Ici on utilise self.admin.id car il a été défini dans setUpClass
        log = self.db.query(AuditLog).filter(
            AuditLog.action == "CRÉATION",
            AuditLog.user_id == self.admin.id 
        ).first()
        
        self.assertIsNotNone(log, "Le log d'audit de création est manquant")
        self.assertIn("AgentTest", log.details)

    def test_02_update_et_audit(self):
        """Vérifie la modification d'un utilisateur et son log d'audit"""
        user = self.db.query(User).filter(User.username == "AgentTest").first()
        success, msg = self.controller.update_user(user.id, {"role": "superviseur"})
        
        self.assertTrue(success)
        log = self.db.query(AuditLog).filter(AuditLog.action == "MISE À JOUR").first()
        self.assertIsNotNone(log)

    def test_03_delete_et_audit(self):
        """Vérifie la suppression et son log d'audit"""
        user = self.db.query(User).filter(User.username == "AgentTest").first()
        success, msg = self.controller.delete_user(user.id)
        
        self.assertTrue(success)
        log = self.db.query(AuditLog).filter(AuditLog.action == "SUPPRESSION").first()
        self.assertIsNotNone(log)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()