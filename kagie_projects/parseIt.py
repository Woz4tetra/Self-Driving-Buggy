
def parseIt(data):
    new_data = data.split(",")
    longitude, latitude = "", ""
    #print new_data
    for i in xrange(len(new_data)):
        if i == 0:
            pass
        elif new_data[i] == "W" or new_data[i] == "E":
            longitude = float(new_data[i-1])
        elif new_data[i] == "N" or new_data[i] == "S":
            latitude = float(new_data[i-1])
    print("longitude: %s"% longitude)
    print("latitude: %s"% latitude)
    return (latitude,longitude)


output = '''$GPGGA,181908.00,3404.7041778,N,07044.3966270,W,4,13,1.00,495.144,M,29.200,M,0.10,0000*40'''
#parseIt(output)

def close(bind, pos, acc):
    #take a bind spot and position from gps
    #and see if they are close enough to be correct
    dist_lat = abs(bind[0]-pos[0])
    dist_lng = abs(bind[1]-pos[1])
    dist = ((dist_lat**2) + (dist_lng**2)**(0.5))
    print dist
    if dist > acc:
        return False
    elif dist <= acc:
        return True
    

def bind(track, pos, acc, prev_bind = 0):
    #REQUIRES: track is a list of tuple (lat, lng)
    #REQUIRES: pos = (lat,lng) are within (accuracy) units of a bind point
    #REQUIRES prev_bind is in boundary of track
    #ENSURES: will find closest bind point and return position of it and #
    print len(track), "num of bind points"
    if prev_bind >= len(track):
        raise Exception("bind outside track")
    for i in xrange(prev_bind,len(track)):
        if close(track[i],pos,acc) == True:
            return (track[i], i)
    for i in xrange(len(track)):
        if close(track[i],pos,acc) == True:
            return (track[i], i)
    return 


def test(string):
    pos = parseIt(string)
    print pos, "pos in test"
    track = [(3404.704179,7044.3967), (3404.7046,7044.3692)]
    acc = 0.05
    (new_pos, num_bind) = bind(track, pos, acc)
    print new_pos, num_bind, "new_pos and num_bind"

test(output)
