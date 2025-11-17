"""
Script utilitaire pour générer des mots de passe hashés
pour l'authentification de l'application
"""
import streamlit_authenticator as stauth
import sys


def generate_password_hash(password: str) -> str:
    """Génère le hash bcrypt d'un mot de passe"""
    hashed = stauth.Hasher([password]).generate()[0]
    return hashed


if __name__ == "__main__":
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = input("Entrez le mot de passe à hasher : ")
    
    hashed = generate_password_hash(password)
    print(f"\nMot de passe hashé : {hashed}")
    print("\nCopiez cette valeur dans votre fichier secrets.toml")

