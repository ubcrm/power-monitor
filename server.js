let express = require('express');
let app = express();

let port = process.env.PORT || 8080;

let postBodies = [];

let initialTime = 0;

app.use(express.static(__dirname));

app.get("/", function(req, res) {
  res.render("index");
});

app.get("/getVals", function(req, res) {
  if (Array.isArray(postBodies) && postBodies.length) {   
    postBodies.sort((body_a, body_b) => body_a.time - body_b.time);

    let responseJSON = postBodies[0];
    responseJSON.time = responseJSON.time - initialTime;
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
  res.send("OK");
});

app.post("/updateVals", function(req, res) {
  let reqJSON = req.body;
  console.log(reqJSON);
  postBodies.push(reqJSON);

  console.log("received, ", postBodies);
  if (!(Array.isArray(postBodies) && postBodies.length)) {
    initialTime = reqJSON.time;
  }

  res.send("OK");
});

app.listen(port, function() {
  console.log("app running");
})

