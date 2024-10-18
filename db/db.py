import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

conection = None

try:
    conection = pymongo.MongoClient(os.getenv('DATABASE_URL'))
except:
    print("No se conecto a la base de datos")

usuarios =  conection['citas']
usuarios = usuarios['usuarios']
