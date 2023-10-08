import json, glob, shutil, sys, math

def format_lrc_timestamp(ms):
    secs = round(ms / 1000, 2)
    secs_remainder = math.floor(secs) % 60
    mins = round((secs - secs_remainder) / 60)
    return "[" + str(mins).zfill(2) + ":" + str(round(secs - (mins * 60), 2)).zfill(5) + "]"

files = []

try:
    files = sys.argv[1:]
except:
    files = glob.glob("./downloaded/*")

print("Processing:")
for i in files:
    print(i)

for i in files:
    data = {}

    with open(i) as file:
        data = json.load(file)

    lines = []
    if not data["lyrics"]["synchronizedLines"]:
        print("No synchronized lyrics for '" + data["title"] + "'. Skipping")
        continue;
    for idx in range(0, len(data["lyrics"]["synchronizedLines"]) - 1):
        l = data["lyrics"]["synchronizedLines"][idx]
        next_l = data["lyrics"]["synchronizedLines"][idx + 1]
        line = l["lrcTimestamp"] + " " + l["line"]
        lines.append(line)

        duration = l["duration"]
        ms = l["milliseconds"]
        next_ms = next_l["milliseconds"]

        gap = next_ms - (ms + duration)

        if (gap > 500):
            print("GAP DETECTED @ " + line)
            print("gap size: ", str(gap) + " ms")
            gap_start_ms = ms + duration

            lines.append(format_lrc_timestamp(gap_start_ms))

    l = data["lyrics"]["synchronizedLines"][-1]
    lines.append(l["lrcTimestamp"] + " " + l["line"])

    for j in range(0, len(lines) - 1):
        lines[j] += "\n"

    with open("./processed/" + data["title"] + ".lrc", "w") as file:
        file.writelines(lines)

    shutil.move(i, "./finished/" + data["title"] + ".dlrc")

print("Finished!")
