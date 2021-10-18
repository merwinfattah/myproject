from datetime import timedelta
from fastapi import FastAPI,HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import crud, schemas
import json


with open("menu.json","r") as read_file:
	data = json.load(read_file)

fake_users_db = {
"johndoe": {
        "username": "johndoe",
		"password": "123"
}
}

ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app = FastAPI()
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, crud.SECRET_KEY, algorithms=[crud.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = username
    except JWTError:
        raise credentials_exception
    user = crud.get_user(fake_users_db, username=token_data)
    if user is None:
        raise credentials_exception
    return user


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/")
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user


@app.get('/menu/{item_id}') # Lihat  menu
async def read_menu(item_id: int):
	for menu_item in data['menu']:
		if menu_item['id'] == item_id:
			return menu_item
	raise HTTPException(
			status_code=404, detail=f'Item not found'
			)

@app.post('/menu') # Tambah menu
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
	with open("menu.json","w") as write_file:
        	json.dump(data,write_file,indent=4)
	write_file.close()

	return(menu_baru)



@app.put('/menu/{item_id}') # Ubah menu
async def update_menu(item_id:int, name:str):
	for menu_item in data['menu']:
		if menu_item['id'] == item_id :
			menu_item['name'] = name # assign nama menu baru ke nama menu pada id terkait yang telah ada
			read_file.close()
			with open('menu.json','w') as write_file:
				json.dump(data,write_file,indent=4)
			write_file.close()

			return{"message":"Menu diubah"}

@app.delete('/menu/{item_id}')  # Hapus Menu
async def delete_menu(name: str):
	for menu_item in data['menu']:
		if menu_item['name'] == name :
			data['menu'].remove(menu_item) # hapus menu dari list menu pada file menu.json
			read_file.close()
			with open('menu.json','w') as write_file:
				json.dump(data,write_file,indent=4)
			write_file.close()

			return{"message":"Menu dihapus"}
	


