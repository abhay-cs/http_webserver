#!/usr/bin/python3

import sys
import socket
import json
import uuid
import threading


HOST = '127.0.0.1'
PORT = int(sys.argv[1])


# file path names
API_PATH = '/api/memo'
database = './db/database.json'
FILE = './files'
IMAGES = './files/images'
INDEX = '/index.html'


# check if the request is valid or not
def isValidRequest(request):
    if request[0] == 'GET' or 'POST' or 'PUT' or "DELETE":
        return True



# check if the incoming request is valid or not

def isValidAPI(request):
    if API_PATH in getRequestPath(request):
        return True
    return False


# check for valid image requests by checking the image path

def isValidImage(request):
    if '/images.html' in getRequestPath(request):
        return True


# returns a response header according to the type of request that we got

def generateHeader(code, contentType, contentLength, request):

    if code == 200:
        if(checkCookie(request)):
            return f"HTTP/1.1 200 OK\nContent-Type:{contentType}\nContent-Length:{contentLength}\n\n"
        else:
            cookieID = str(uuid.uuid4())
            return f"HTTP/1.1 200 OK\nContent-Type:{contentType}\nContent-Length:{contentLength}\nSet-Cookie: id={cookieID}\n\n"
    elif code == 404:
        return "HTTP/1.1 404 NOT FOUND\r\n"
    elif contentType == 'none':
        return "HTTP/1.1 200 OK\r\n"
    else:
        return "INVALID CODE"

# DEBUG[print the incoming request]
def printRequest(request):
    print(request[0] + " " + request[1] + " " + request[2])

# decode the incoming data and return the request
def parseRequest(data):
    request = data.decode()
    return request.split()

# grabs the path of the request
def getRequestPath(request):
    return request[1]

# checks what king of request is it??
def getRequestType(request):
    return request[0]


def checkCookie(request):
    if 'Cookie:' in request:
        return True
    return False


def getCookieID(request):

    index = request.index("Cookie:")
    return request[index+1]

# add the memo to database
def addMemo(entry, request):
    # generates a random id for each memo
    cookie = str(getCookieID(request))
    entry['id'] = str(uuid.uuid4())[:8]
    entry['last-edited-by'] = cookie
    data = []

    with open(database, 'r+') as file:
        data = json.load(file)
        data.append(entry)
        file.seek(0)
        json.dump(data, file, sort_keys=True, indent=4, separators=(',', ': '))

# update the memo based on memo id
def updateMemo(memoID, obj, new, request):

    for i in range(len(obj)):

        if obj[i]['id'] == memoID:
            obj[i]['text'] = new['text']
            obj[i]['last-edited-by'] == 'abhay=sharma'
            break

    open(database, 'w').write(
        json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))
    )

# returns the memo id
def getMemoID(request):
    return getRequestPath(request).split('/')[3]

# delete the memo based on id
def deleteMemo(id, obj):

    for i in range(len(obj)):
        if obj[i]['id'] == id:
            obj.pop(i)
            break

    open(database, 'w').write(
        json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': ')))

# handles the POST request
def handlePOST(request):
    # extract the json from the req
    decoded = request.decode()
    data = (decoded.partition('\r\n\r\n')[2])
    # update/add the db
    postData = json.loads(data)
    addMemo(postData, request)

# handles the PUT request
def handlePUT(request, path):

    memoID = getMemoID(request)
    decoded = path.decode()
    putData = (decoded.partition('\r\n\r\n')[2])
    data = json.load(open(database))
    newData = json.loads(putData)
    print(newData)
    updateMemo(memoID, data, newData, request)

# handles the DELETE request
def handleDELETE(request):

    memoID = getMemoID(request)
    obj = json.load(open(database))
    deleteMemo(memoID, obj)

#  function to read the HTML doc
def readFile(fileToRead):
    file = open(fileToRead, 'r')
    output = file.read()
    file.close()
    return output

# main chunck to handle incoming requests
def handleAPI(conn, request, data):

    if(getRequestType(request) == 'GET'):

        body = readFile(database)
        head = generateHeader(200, 'application/json', len(body), request)
        response = head + body
        conn.sendall(response.encode('utf-8'))
        conn.close()

    elif(getRequestType(request) == 'POST'):

        handlePOST(data)

        response = generateHeader(200, 'none', 0, request)
        conn.sendall(response.encode('utf-8'))
        conn.close()

    elif(getRequestType(request) == 'PUT'):

        handlePUT(request, data)

        response = generateHeader(200, 'none', 0, request)
        conn.sendall(response.encode('utf-8'))
        conn.close()

    elif(getRequestType(request) == 'DELETE'):

        handleDELETE(request)

        response = generateHeader(200, 'none', 0, request)
        conn.sendall(response.encode('utf-8'))
        conn.close()


def handleFiles(conn, request):
    if (getRequestType(request) == 'GET'):

        if (getRequestPath(request) == '/' or getRequestPath(request) == INDEX):
            filename = FILE + INDEX
            body = readFile(filename)
            head = generateHeader(200, "text/html", len(body), request)
            response = head + body
            conn.sendall(response.encode())

        # handles images
        if('.jpeg' in getRequestPath(request) or isValidImage(request)):

            if('.jpeg' in getRequestPath(request)):
                filename = FILE + getRequestPath(request)
                # read image on the fly
                file = open(filename, 'rb')
                body = file.read()
                file.close()

                head = generateHeader(200, 'image/jpeg', len(body), request)

                conn.sendall(head.encode())
                conn.sendall(body)
            elif(isValidImage(request)):
                filename = FILE + getRequestPath(request)
                body = readFile(filename)
                head = generateHeader(200, 'text/html', len(body), request)
                response = head + body
                conn.sendall(response.encode('utf-8'))
            else:
                head = generateHeader(404, 'text/html', len(body), request)

    elif(getRequestType(request) == 'POST'):

        postData = request

    else:
        response = generateHeader(404, 'none', 0, request)
        conn.sendall(response.encode('utf-8'))
        print("NOT FOUNxD 404")


def handleRequest(conn, request, data):

    if(isValidRequest(request) == True):
        if(isValidAPI(request) and checkCookie(request)):
            handleAPI(conn, request, data)
        else:
            handleFiles(conn, request)
    else:
        print("Sent request INVALID!! ")


def handleClient(conn, addr):

    print(f"\nconnected by {addr}")
    data = conn.recv(2048)
    request = parseRequest(data)
    printRequest(request)
    handleRequest(conn, request, data)


def start(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen()
    try:
        while True:
            print(f"\nActive threads: {threading.active_count()}")
            conn, addr = s.accept()
            thread_new = threading.Thread(
                target=handleClient, args=(conn, addr))
            thread_new.start()
            thread_new.join()
    except KeyboardInterrupt:
        print("\nRIP\n")
        sys.exit()

# start the server.. 
start(HOST, PORT)
