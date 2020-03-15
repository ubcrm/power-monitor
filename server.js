let express = require('express');
let bodyParser = require('body-parser')
let app = express();

let port = process.env.PORT || 8080;

let postBodies = [];

let initialTime = 0;
let currentTime = 0;
let setToZero = false;

app.use(express.static(__dirname));
// parse application/json
app.use(bodyParser.json())
 
// app.use(app.router);

app.get("/", function(req, res) {
  res.render("index");
});

app.get("/getVals", function(req, res) {
  if (Array.isArray(postBodies) && postBodies.length) {   
    postBodies.sort((body_a, body_b) => body_a.time - body_b.time);

    let responseJSON = postBodies[0];
    responseJSON.time = responseJSON.time - initialTime;
    currentTime = responseJSON.time;

    postBodies.shift();
    console.log("sending, ", postBodies);
    res.json(responseJSON);
  } else {
    res.json("NOT AVAILABLE");
  }
});

app.get("/resetTime", function(req, res) {
  initialTime = 0;
  postBodies = [];

  console.log("time reset, ", postBodies);
  setToZero = true;
  res.send("OK");
});

app.post("/updateVals", function(req, res) {
  console.log(req.body);
  let reqJSON = req.body
  // console.log(reqJSON);
  postBodies.push(reqJSON);
  if (currentTime < reqJSON.time) {
    setToZero = false;
  }

  console.log("received, ", postBodies);
  if (!(Array.isArray(postBodies) && postBodies.length)) {
    initialTime = reqJSON.time;
    console.log("initial time: ", initialTime);
  }

  res.send("OK " + String(setToZero));
});

app.listen(port, function() {
  console.log("app running");
})

