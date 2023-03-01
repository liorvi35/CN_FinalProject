import firebase_admin

from firebase_admin import credentials
from firebase_admin import db

cred_obj = firebase_admin.credentials.Certificate('cn-finalproject-firebase-adminsdk-7l46z-b80e456cf4.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL': 'https://cn-finalproject-default-rtdb.firebaseio.com'
	})

# set - reset data in the database
users_ref = db.reference('users/')
users_ref.set({

    'user1': {
        'name': 'yoad',
        'grade': 100
    },
    'user2': {
        'name': 'lior',
        'grade': 0
    }
})

# update - add new data / update exist data
users_ref.update({
    'user4': {
        'name': 'user4',
        'grade': 12
    }
})

hopper_ref = users_ref.child('user1')
hopper_ref.update({
    'nickname': 'the greatest student'
})

# delete - delete specific data
users_ref.child('user2').delete()

# get
handle = db.reference('users/user1').get()
print(handle)

