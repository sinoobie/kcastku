import requests, os, sys, time
from bs4 import  BeautifulSoup as BS
from tqdm import tqdm

head={
	"Host": "komikcast.com",
    "user-agent": "Mozilla/5.0 (Linux; Android 7.0; Redmi Note 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/45.06.4.5043",
    "sec-fetch-mode": "navigate",
    "accept": "*/*",
    "sec-fetch-site": "same-origin",
    "referer": "https://komikcast.com/daftar-komik/",
    "accept-language": "id-ID,id;q\u003d0.9,en-US;q\u003d0.8,en;q\u003d0.7",
}

def req_data():
	req=requests.get("https://komikcast.com/daftar-komik/?list", headers=head)
	bs=BS(req.text, 'html.parser')
	data=bs.find_all('a',{'class':'series'})
	hsil=[{"title":x.text.strip(), "url":x["href"]} for x in data]
	return hsil

def get_capter(url):
	_cap=[]
	req=requests.get(url,headers=head)
	bs=BS(req.text, 'html.parser')
	data=bs.find_all('span', {'class':'leftoff'})
	for x in data:
		nc=x.text.strip().split(' ')[1]
		if '-' in nc:
			ncp=float(nc.split('-')[0])
		else:
			ncp=float(nc)
		_cap.append([ncp, x.find('a')['href']])
	_cap.sort()
	hsil=[{'cap':y[0], 'url':y[1]} for y in _cap]
	return hsil

def download(url, title, nochap, noimg):
	hder={
		'Host':'cdn.komikcast.com',
		'user-agent':'Mozilla/5.0 (Linux; Android 7.0; Redmi Note 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/45.06.4.5043',
		'accept':'*/*',
		}
	r = requests.get(url, headers=hder, stream=True)
	total_size = int(r.headers.get('content-length', 0))
	print(f"\n# Downloading '{title}/chapter{nochap}'")
	print(f"[{url}]")
	block_size = 1024
	t=tqdm(total=total_size, unit='iB', unit_scale=True)
	with open(f'{MAINDIR}/{title}/chapter{nochap}/'+'{:02}'.format(noimg)+'.jpg','wb') as f:
		for data in r.iter_content(chunk_size=block_size):
			if data:
				t.update(len(data))
				f.write(data)
	t.close()

def get_udl(url, title, nochap):
	try:
		os.mkdir(f"{MAINDIR}/{title}")
	except: pass
	try:
		os.mkdir(f'{MAINDIR}/{title}/chapter{nochap}')
	except: pass
	req=requests.get(url, headers=head)
	bs=BS(req.text, 'html.parser')
	imgs=bs.find_all('img', {'style':'display:none;visibility:hidden;'})
	n=1
	for i in imgs:
		if 'cdn.komikcast.com' in i['data-cfsrc']:
			download(i['data-cfsrc'], title, nochap, n)
			n+=1

def chap_dl(data, lih, title):
	if '-' in lih:
		plih=lih.split('-')
		if len(plih) == 2 and plih[1] != '':
			pil=range(int(plih[0]), int(plih[1])+1)
		else:
			pil=range(int(plih[0]), len(data)+1)
	else:
		get_udl(data[int(lih)-1]['url'], title, int(lih))
		return True

	for x in pil:
		get_udl(data[x-1]['url'], title, x)



print("Get query data...")
data=req_data()
print("OK")
time.sleep(0.5)
os.system('clear')

print("""\033[97m
	[ KOMIKCAST DOWNLOADER ]
	       - noobie -
""")
try:
	open('/sdcard/test.txt','w')
except:
	print("\033[97mNote: Program ini membutuhkan akses internal storage untuk menyimpan hasil download")
	os.system('termux-setup-storage')

MAINDIR='/sdcard/kcastku'
try:
	os.mkdir(MAINDIR)
except: pass
time.sleep(1)

n=1
url=[]
tit=[]
inp=input("Cari: ")
for x in data:
	if inp.lower() in x['title'].lower():
		print(f"{n}. {x['title']}")
		url.append(x['url'])
		tit.append(x['title'])
		n+=1
if len(tit) == 0:
	sys.exit("Manga Tidak Tersedia")
else:
	pil=int(input("Pilih: "))

cap=get_capter(url[pil-1])
print(f"\n\t\033[96m[{len(cap)} Chapter ditemukan]\n\n[Note] Mungkin jumlah chapternya terlihat lebih banyak atupun lebih sedikit dari pada aslinya, itu karena jika ada chapter (misal: 10.5) chapter tsb akan menjadi chapter11 (dibulatkan keatas). ataupun jika ada chapter gabungan (misal: 14-15) kedua chapter ini akan dijadikan satu nama (chapter14)\n")
lih=input("""\033[97m[info]
# ketik (misalnya: 10-) untuk mendownload dari chapter 10 sampai akhir chapter
# ketik (misalnya: 10-20) untuk mendownload dari chapter 10 sampai chapter 20
# ketik angka saja tanpa garis untuk mendownload salah satu chapter
noobie_> """)
chap_dl(cap, lih, tit[pil-1])
print("\n\033[92m[all done] Semua hasil downloadnya tesimpan di internal storage (/sdcard/kcastku)")
