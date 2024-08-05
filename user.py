from modal.authMysql import BDD_MYSQL
import bcrypt
import base64

bddUser = BDD_MYSQL('user')

pseudo = input('Entrer pseudo: ')
enter = input('Entrer mot de pase: ')
agence = input('Entrer agence: ')
niveau = input('Grade: ')

# Hacher un mot de passe
password = enter.encode('utf-8')
hashed = bcrypt.hashpw(password, bcrypt.gensalt())

# Convertir le hash en une chaîne encodée en Base64 pour JSON
hashed_str = base64.b64encode(hashed).decode('utf-8')


test = bddUser.postData(
    arg=[
            {
                "pseudo": pseudo,
                "mdp": hashed_str,
                "agence": agence,
                "role": niveau
            }
        ]
    )

if test:
    print('ok')
