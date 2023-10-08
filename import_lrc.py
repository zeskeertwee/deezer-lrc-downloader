import copy, sqlite3, os, pathlib, shutil
from Levenshtein import distance as lev

def find_closest_match(tracks, query):
    closest = 1000
    closest_item = ""

    for i in tracks:
        if lev(query, i[1]) < closest:
            closest = lev(query, i[1])
            closest_item = copy.deepcopy(i)

    return closest_item

db_file = os.path.expanduser("~/Music/library.db")
print('Opening library database @ ' + db_file)
con = sqlite3.connect(db_file)
con.text_factory = lambda x: x.decode("utf-8")
cur = con.cursor()
res = cur.execute("select path, title, album from items")
tracklist = res.fetchall()
print("Loaded " + str(len(tracklist)) + " tracks from the library")

ops = []

for i in range(0, len(tracklist)):
    tracklist[i] = list(tracklist[i])
    tracklist[i][0] = tracklist[i][0].decode('utf-8')
    

for i in os.listdir('./processed'):
    path = pathlib.Path(i)
    trackname = path.parts[-1].replace('.lrc', '')
    closest = find_closest_match(tracklist, trackname)
    print(trackname + ' --> ' + str(closest[1]))
    if not closest[0].endswith('.flac'):
        print('WARN ' + str(closest) + " does not end in .flac, skipping")
        continue
    
    ops.append((i, closest[0].replace('.flac', '.lrc')))
    
if input('Are these mappings okay? (y/n) ').lower() == 'y':
    for op in ops:
        shutil.copy('./processed/' + op[0], op[1])
        print('moved ' + str(op[0]) + ' --> ' + str(op[1]))
        
else:
    print('exit')
