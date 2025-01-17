from pymongo import MongoClient, ReturnDocument
from pymongo.errors import ConnectionFailure
from data.definitions import Item, User, ClothList
from starlette.responses import JSONResponse
import json


#client = MongoClient("mongodb+srv://admin:27remb3jZ5FKY31f@okapi-adviser-cluster-vcqku.gcp.mongodb.net/test?retryWrites=true&w=majority")
#db = client.get_database(name='adviser-db')

class Database:
    def __init__(self):
        self.client = MongoClient("mongo:27017", username='root', password='root')
        self.db = self.client.get_database(name='adviser')

    # Métodos na coleção de utilizadores

    def add_like(self, user_id: int, item_id: int):
        users_likes = self.db.get_collection(name='likes')
        catalog = self.db.get_collection(name='catalog')
        
        if not users_likes.find_one(filter={'user_id':user_id}):
            return "User not found."

        if not catalog.find_one(filter={'item_id':item_id}):
            return "Item not found."
        
        new_like = catalog.find_one(filter={'item_id':item_id})

        users_likes.update_one(filter={'user_id':user_id}, update={'$push':{'likes.'+new_like['body_part'] : new_like}})
        return "Inserted!"
    
    def add_user(self, user: dict):
        likes = self.db.get_collection('likes')
        new_user = {"user_id":user['id'], "user_gender": user['gender'],"likes":{"upper":[],"cover":[],"bottom":[],"feet":[]}}
        likes.insert_one(new_user)
        return "Inserted"

        
    def rm_like(self, user_id: int, item_id: int):
        users_likes = self.db.get_collection(name='likes')
        catalog = self.db.get_collection(name='catalog')

        if not catalog.find_one(filter={'item_id':item_id}):
            return "Item not found."

        body_part = catalog.find_one(filter={'item_id':item_id})['body_part']


        users_likes.update_one(filter={'user_id':user_id}, update= {'$pull': {'likes.'+body_part:{'item_id':item_id}} })
        return "Deleted!"

    def get_user(self, user_id:int):
        likes = self.db.get_collection('likes')
        if not likes.find_one(filter={'user_id':user_id}, projection= {'_id':0}):
            return None

        return likes.find_one(filter={'user_id':user_id}, projection= {'_id':0})
    
    # Métodos na coleção do catálogo
    
    def get_item(self, item_id: int):
        catalog = self.db.get_collection('catalog')
        if not catalog.find_one(filter={'item_id':item_id}, projection={'_id':0}):
            return None

        return catalog.find_one(filter={'item_id':item_id}, projection={'_id':0})
    
    def get_items(self, gender: str, body_part: str):
        return self.db.get_collection('catalog').find(filter={'gender':gender, 'body_part':body_part}, projection={'_id':0})

    def add_item(self, item: Item):
        self.db.get_collection('catalog').insert_one(dict(item))
        return 'Done'

    # Métods na coleção dos outfits 

    def add_rating(self, outfit: dict):
        self.db.get_collection('outfits').insert_one(outfit)
        return 'Rated'


    """     def add_likes(self, user_id:int, new_likes: ClothList):
        users_likes = self.db.get_collection(name='likes')
        if not users_likes.find_one(filter={'user_id':user_id}):
            new_user = {"user_id":user_id,"user_likes":{"upper":[],"cover":[],"bottom":[],"feet":[]}}
            users_likes.insert_one(new_user)

        users_likes.update_one(filter={'user_id':user_id}, 
                update={'$push':{'user_likes.upper' : {'$each': [ json.loads(like.json()) for like in new_likes.upper] }}})
        users_likes.update_one(filter={'user_id':user_id}, 
                update={'$push':{'user_likes.cover' : {'$each': [ json.loads(like.json()) for like in new_likes.cover] }}})
        users_likes.update_one(filter={'user_id':user_id}, 
                update={'$push':{'user_likes.bottom' : {'$each': [ json.loads(like.json()) for like in new_likes.bottom] }}})
        users_likes.update_one(filter={'user_id':user_id}, 
                update={'$push':{'user_likes.feet' : {'$each': [ json.loads(like.json()) for like in new_likes.feet] }}})
        
        return 'Inserted' """