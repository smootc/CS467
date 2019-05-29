import config
import records

#---------------------------------------------------
#establish connection with database
#---------------------------------------------------
def connectDB():
    return records.Database('postgresql://{user}:{pw}@{url}/{dbName}'.format(user=dbconfig.POSTGRES_USER, pw=dbconfig.POSTGRES_PW, url=dbconfig.POSTGRES_URL, dbName=dbconfig.POSTGRES_DB))
