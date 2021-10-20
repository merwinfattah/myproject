
from fastapi import FastAPI,HTTPException, Depends
import auth, schemas
import json


with open("restodata.json","r") as read_file:
	data = json.load(read_file)



auth_handler = auth.AuthHandler()



app = FastAPI()

@app.get('/')
async def read_root():
	return {"message":"Muhammad Erwin Fattah/ 18219019. tambahkan  /docs pada url untuk endpoints."}


@app.post('/register', status_code=201)
async def register(auth_details: schemas.AuthDetails):
    if any(user['username'] == auth_details.username for user in data["users"]):
        raise HTTPException(status_code=400, detail='Username is taken')
    hashed_password = auth_handler.get_password_hash(auth_details.password)
    new_user={'username': auth_details.username,'password': hashed_password}
    data["users"].append(new_user)
    read_file.close()
    with open("restodata.json","w") as write_file:
        	json.dump(data,write_file,indent=4)
    write_file.close()
    return {"message" : "You're registered"}


@app.post('/login')
async def login(auth_details: schemas.AuthDetails):
    user = None
    for userInDB in data["users"]:
        if userInDB['username'] == auth_details.username:
            user = userInDB
            break
    
    if (user is None) or (not auth_handler.verify_password(auth_details.password, user['password'])):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(user['username'])
    return { 'token': token }

@app.get('/menu/{item_id}', dependencies=[Depends(auth_handler.auth_wrapper)]) # Lihat  menu
async def read_menu(item_id: int):
	for menu_item in data['menu']:
		if menu_item['id'] == item_id:
			return menu_item
	raise HTTPException(
			status_code=404, detail=f'Item not found'
			)

@app.post('/menu', dependencies=[Depends(auth_handler.auth_wrapper)]) # Tambah menu
async def post_menu(name:str):
	id=1 # inisiasi id untuk menu yang ingin ditambahkan
	idx=0 # inisiasi indeks penempatan menu dalam list
	tempListId = [] # inisiasi list sementara
	for i in range(len(data['menu'])) : # pengisian list sementara
		tempListId.append(id)
		id+=1
	if(len(data['menu'])>0): # pencarian id dan indeks untuk menu baru
		for i in range(len(data['menu'])):
			if data['menu'][i]['id'] != tempListId[i] :
				id = tempListId[i]
				idx = i
				break

	menu_baru={'id':id,'name':name}
	data['menu'].insert(idx,dict(menu_baru)) # menambahkan menu dalam list menu di file menu.json
	read_file.close()
	with open("restodata.json","w") as write_file:
        	json.dump(data,write_file,indent=4)
	write_file.close()

	return(menu_baru)



@app.put('/menu/{item_id}' , dependencies=[Depends(auth_handler.auth_wrapper)]) # Ubah menu
async def update_menu(item_id:int, name:str):
	for menu_item in data['menu']:
		if menu_item['id'] == item_id :
			menu_item['name'] = name # assign nama menu baru ke nama menu pada id terkait yang telah ada
			read_file.close()
			with open('restodata.json','w') as write_file:
				json.dump(data,write_file,indent=4)
			write_file.close()

			return{"message":"Menu diubah"}

@app.delete('/menu/{item_id}', dependencies=[Depends(auth_handler.auth_wrapper)])  # Hapus Menu
async def delete_menu(name: str):
	for menu_item in data['menu']:
		if menu_item['name'] == name :
			data['menu'].remove(menu_item) # hapus menu dari list menu pada file menu.json
			read_file.close()
			with open('restodata.json','w') as write_file:
				json.dump(data,write_file,indent=4)
			write_file.close()

			return{"message":"Menu dihapus"}
	


