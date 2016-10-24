var http = require('http'),
    fs = require('fs');


fs.readFile('testapp/node_modules/public/index.html', function (err, html) {
    if (err) {
        throw err; 
    }

var spawn = require('child_process').spawn,
    py    = spawn('python', ['../pythoncode/NBAparser.py']),
    data = [1,2,3,4,5,6,7,8,9],
    test = {};
    dataString = '';
    
    py.stdout.on('data', function(data){
        dataString += data.toString();

    });
    py.stdout.on('end', function(){
        console.log('JSON=',dataString);
        console.log('tester=',JSON.parse(dataString));
        test = JSON.parse(dataString);
    });
         
    http.createServer(function(request, response) {  
        response.writeHeader(200, {"Content-Type": "text/html"});  
        response.write('<html><body><h1> Test</h1>');
        response.write(test.jwins.toString());  
        response.write('</body></html>');
        response.end();  
    }).listen(8000);
});






