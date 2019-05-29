import config
import records

#---------------------------------------------------
#establish connection with database
#---------------------------------------------------
def connectDB():
    return records.Database('postgresql://{user}:{pw}@{url}/{dbName}'.format(user=config.POSTGRES_USER, pw=config.POSTGRES_PW, url=config.POSTGRES_URL, dbName=config.POSTGRES_DB))
