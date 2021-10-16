from fastapi import FastAPI,HTTPException
import json

with open("menu.json","r") as read_file:
	data = json.load(read_file)

app = FastAPI()

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
	


