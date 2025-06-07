import os

SECRET_KEY = os.environ.get("SECRET_KEY", "supersecret")
SQLALCHEMY_DATABASE_URI = 'sqlite:///jobtracker.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# JWT Security Features (configurable)
JWT_ROTATE_REFRESH_TOKENS = True
JWT_BLACKLIST_ENABLED = True
JWT_DEVICE_BINDING_ENABLED = False
JWT_REFRESH_LIMIT_ENABLED = True