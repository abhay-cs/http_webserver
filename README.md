
# HTTP webserver
### This project was part of the assignment of one of my courses that i took at university.


## How to Run:

```bash
./server.py [port-number] or python3 server.py [port-number]
```

### API works , sets cookies upon GET request and then updates/deletes/add memos on the api path(/api/memo)


## About the project: 

Here I implemented an HTTP webserver with REST API protocol with diffrent Methods such as GET, POST, PUT, DELETE. That we can run on an JSON database and our server handles those requests.  

Here we are using an example of a MEMO system that we can store in a database as a JSON file and can perform operations on those MEMO's using the '/api/memo' path through the web server.

## Testing:

Ran with INSOMNIA to test the /api/memo path 