from pymongo import MongoClient

def get_db():
    client = MongoClient('mongodb+srv://support:JPB2v7xa1rwGmjS8@cluster0.rxj5qey.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    db = client['support']
    return db