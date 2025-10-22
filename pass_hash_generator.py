from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

passwords = {
    "superadmin@qjskills.com": "S@p3rAdm!n#2025",
    "admin@qjskills.com": "Adm!n#Qj2025$",
    "notification@qjskills.com": "N0tify@Qj#2025!",
    "feeds@qjskills.com": "Fe3ds!2025#Qj$",
}

for email, pwd in passwords.items():
    print(email, "→", pwd_context.hash(pwd))
