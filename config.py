import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'student.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ROOT_PATH = basedir
    STATIC_FOLDER = os.path.join(basedir, 'app//static')
    TEMPLATE_FOLDER_MAIN = os.path.join(basedir, 'app//main//templates')
    TEMPLATE_FOLDER_ERRORS = os.path.join(basedir, 'app//errors//templates')
    TEMPLATE_FOLDER_AUTH = os.path.join(basedir, 'app//auth//templates')
    #Microsoft Identity
    AUTHORITY = 'https://login.microsoftonline.com/589c76f5-ca15-41f9-884b-55ec15a0672a'
    CLIENT_ID = 'ee9c7d20-213e-491b-ada9-3d1b01b30504'
    OBJECT_ID = '9c5319da-960c-4f31-be51-2c1a309dcc5d'
    CLIENT_SECRET = '7561d710-6252-4c11-a4f1-526b360d94c8'
    SCOPE = ["User.Read"]
    SESSION_TYPE = "filesystem"
    REDIRECT_PATH = '/getAToken'