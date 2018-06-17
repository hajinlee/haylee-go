var myCanvas = document.getElementById('myboard');
var ctx = myCanvas.getContext('2d');

// Fixing the go board position if necessary
//myCanvas.style.position = 'absolute';
//myCanvas.style.left = '50px';
//myCanvas.style.top = '50px';

var background = new Image();
background.src = "assets/kaya.jpg";

var white_stone = new Image();
white_stone.src = "assets/white.png";

var black_stone = new Image();
black_stone.src = "assets/black.png"

var stone_positions = null;

function drawBoard(board_size) {
  setBoardParams(board_size)

  var board_width = (cell_width * board_size) + (margin * 2);
  var board_height = (cell_height * board_size) + (margin * 2);

  myCanvas.width = board_width;
  myCanvas.height = board_height;

  // draw the board and stone images first
  if(background.complete && white_stone.complete && black_stone.complete) {
    ctx.drawImage( background, 0, 0, board_width, board_height );
  } else {
    // the image has not finished downloading yet.
    // stop here. We will try to draw again when the image finishes,
    // in the "load" event handler.
    return;
  }

/* draw a board with white background:
ctx.beginPath();
ctx.rect(0, 0, board_width, board_height);
ctx.fillStyle = '#ffffff';
ctx.fill(); */

  // Draw vertical lines on the board.
  for (let x=margin; x<=board_height-margin+1; x+=cell_height){
    ctx.strokeStyle = '#000000';
    ctx.beginPath();
    ctx.moveTo( margin, x );
    ctx.lineTo( board_width-margin, x );
    ctx.closePath();
    ctx.lineWidth = 0.5;
    ctx.fillStyle = '#000000';
    ctx.stroke();
  }

  // Draw horizontal lines on the board.
  for (let x=margin; x<=board_width-margin+1; x+=cell_width){
    ctx.strokeStyle = '#000000';
    ctx.beginPath();
    ctx.moveTo( x, margin );
    ctx.lineTo( x, board_height-margin );
    ctx.closePath();
    ctx.lineWidth = 0.5;
    ctx.fillStyle = '#000000';
    ctx.stroke();
  }

  // Draw star points on the board.
  if (board_size === 18) {
    for (let x=(cell_width*3)+margin; x<=(cell_width*15)+margin; x+=cell_width*6){
      starPoint(x, ((cell_height*3)+margin));
      starPoint(x, ((cell_height*9)+margin));
      starPoint(x, ((cell_height*15)+margin));
    }
  }

  if (board_size === 12) {
    starPoint(((cell_width*6)+margin), ((cell_height*6)+margin))
    for (let x=(cell_width*3)+margin; x<=(cell_width*10)+margin; x+=cell_width*6){
      starPoint(x, ((cell_height*3)+margin));
      starPoint(x, ((cell_height*9)+margin));
    }
  }

  if (board_size === 8) {
    starPoint(((cell_width*4)+margin), ((cell_height*4)+margin))
  }

  if(stone_positions) {
    for (let i=0; i<board_size+1; i++) {
      for (let j=0; j<board_size+1; j++) {
        if (stone_positions[i][j] === '@') {
          drawStone('black', j, i, board_size)
        }
        else if (stone_positions[i][j] === 'O') {
          drawStone('white', j, i, board_size)
        }
      }
    }
  }
}

// after the background image finishes loading, redraw the board
background.addEventListener('load', function(event) { drawBoard(); }, true);
white_stone.addEventListener('load', function(event) { drawBoard(); }, true);
black_stone.addEventListener('load', function(event) { drawBoard(); }, true);

function coordToPixel(x, y, board_size) {
  setBoardParams(board_size);
  let x_pos = (x * cell_width) + margin;
  let y_pos = (y * cell_height) + margin;
  return { x: x_pos, y: y_pos };
}

function pixelToCoord(x, y, board_size) {
  setBoardParams(board_size);
  let x_pos = Math.round((x-margin) / cell_width);
  let y_pos = Math.round((y-margin) / cell_height);
  return { x: x_pos, y: y_pos };
}

function onMouseClick(event) {
  event = event || window.event;
  var target = event.target || event.srcElement;
  var rect = target.getBoundingClientRect();
  var offsetX = event.clientX - rect.left;
  var offsetY = event.clientY - rect.top;
  if (event.currentTarget.offsetWidth === 462) {
    let board_size = 18
  } else if (event.currentTarget.offsetWidth === 437.2) {
    let board_size = 12
  } else {
    let board_size = 8
  }
  var pos = pixelToCoord(offsetX, offsetY, board_size);
  console.log(offsetX, offsetY, pos.x, pos.y);

  // check if the "remove dead stones" controls are visible
  var remove_div = document.getElementById('remove');
  if (remove_div.style.display != 'none') {
    var rbox = document.getElementById('remove_this');
    rbox.value = rbox.value + ' ' + pos.y.toFixed(0) + ',' + pos.x.toFixed(0); // click to select dead
  }
  else {
    clickToSubmitXHR(pos.y, pos.x); // click to play
  }
}

function starPoint(x_pos, y_pos) {
  ctx.beginPath();
  ctx.arc(x_pos,y_pos,3,0,2*Math.PI);
  ctx.fill();
}

function drawStone(color, x, y, board_size) {
  let pos = coordToPixel(x, y, board_size);
  var img = color === 'white' ? white_stone : black_stone;
  if (board_size === 18) {
    ctx.drawImage(img, pos.x - 11, pos.y - 11, 22, 22);
  } else if (board_size === 12) {
    ctx.drawImage(img, pos.x - 17, pos.y - 17, 32, 32);
  } else if (board_size === 8) {
    ctx.drawImage(img, pos.x - 20, pos.y - 20, 40, 40);
  }
}

/* Draw stone using an arc:
ctx.beginPath();
ctx.arc(pos.x,pos.y,11,0,2*Math.PI);
ctx.stroke();
ctx.fillStyle = color;
ctx.fill();
*/

myCanvas.addEventListener('click', onMouseClick, true);
//window.addEventListener('resize', function(event) { drawBoard(); }, true);

/*
function clickToSubmit(x, y) {
  var xbox = document.getElementById('xcoord');
  xbox.value = x.toFixed(0);
  var ybox = document.getElementById('ycoord');
  ybox.value = y.toFixed(0);
  var submit_button = document.getElementById('submit');
  submit_button.click();
}
*/

// given a list of strings like ["+++@++", ...],
function updateBoard(board_js) {
  // update the stone positions
  stone_positions = [];
  let new_board_size = board_js.length; // this is probably 19 or 9
  board_size = new_board_size - 1; // because we use the convention that 19x19 -> board_size = 18

  for(let i = 0; i < board_size+1; i++) {
    stone_positions.push(board_js[i]);
  }
  // redraw the board
  drawBoard(board_size);
}

function setBoardParams(board_size) {
  if (board_size === 18) {
    cell_height = 26;
    cell_width = 24;
    margin = 15;
  }

  else if (board_size === 12) {
    cell_height = 26 * 1.4;
    cell_width = 24 * 1.4;
    margin = 17;
  }

  else if (board_size === 8) {
    cell_height = 26 * 1.8;
    cell_width = 24 * 1.8;
    margin = 19;
  }
}

// Different options
function clickToSubmitXHR(xcoord, ycoord) {
  sendXHR({'command': 'New Move', 'xcoord': xcoord, 'ycoord': ycoord});
}
function passXHR() {
  sendXHR({'command': 'Pass'});
}

function undoXHR() {
  sendXHR({'command': 'Undo'});
}

function resignXHR() {
  sendXHR({'command': 'Resign'});
}

function newGameXHR(board_size) {
  sendXHR({'command': 'New Game', 'board_size': board_size});
}

function removeXHR(need_remove) {
  sendXHR({'command': 'Dead Stones', 'dead': need_remove});
}

function uploadSGFXHR(sgf_string) {
  sendXHR({'command': 'Upload SGF', 'sgf': sgf_string});
}

function downloadSGF(sgf_string) {
  window.open('./sgf', '_blank');
}

function sendXHR(params) {
  const xhr = new XMLHttpRequest();
  const url = './'; // send request to the current URL
  const data = JSON.stringify(params);

  xhr.responseType = 'json';
  xhr.onreadystatechange = function() {
	   if (xhr.readyState === XMLHttpRequest.DONE) {
       let response = xhr.response; // <-- this is the JSON we got back from the server

       // show board
       let myboard = document.getElementById('myboard');
       if (response['board_js']) {
         myboard.style.display = 'block';
       }

       // refresh the browser UI according to the latest server response:
       updateBoard(response['board_js']);

       // show illegal message when appropriate
       let illegal = document.getElementById('illegal_move_message');
       if (response['illegal']) {
         illegal.style.display = 'block';
       } else {
         illegal.style.display = 'none';
       }

       // ask to select and submit the captured stones
       let remove = document.getElementById('remove');
       if (response['game_state'] === 'SCORING' && response['removed'] === false) {
          remove.style.display = 'block';
       } else {
         remove.style.display = 'none';
       }

       // show the result when appropriate
       let result = document.getElementById('result');
       if(response['result'] !== " ") {
         result.style.display = 'block';
         result.innerHTML = response['result'];
       } else {
         result.style.display = 'none';
       }

       // fun greeting messages
       let greet = document.getElementById('greeting_message');
       if (response['game_state'] === 'PLAYING') {
         greet.innerHTML = response['greeting'];
       } else if (response['game_state'] === 'SCORING') {
         greet.innerHTML = 'That was a tough game!';
       } else if (response['game_state'] === 'OVER') {
         greet.innerHTML = 'Thank you for the game!';
       } else {
         greet.innerHTML = 'Hello! How about a nice game of Go?';
       }

       // whose turn?
       let turn = document.getElementById('turn');
       if (response['game_state'] === 'PLAYING') {
         turn.style.display = 'block';
         turn.innerHTML = response['turn'] + ' to play';
       } else {
         turn.style.display = 'none';
       }

       // hide buttons when they are not needed
       let pass = document.getElementById('pass');
       let undo = document.getElementById('undo');
       let resign = document.getElementById('resign');
       let sgf_down = document.getElementById('sgf_down');
       let sgf_up = document.getElementById('sgf_up');
       if (response['game_state'] === 'PLAYING') {
         pass.style.display = 'inline-block';
         undo.style.display = 'inline-block';
         resign.style.display = 'inline-block';
         sgf_down.style.display = 'inline-block';
         sgf_up.style.display = 'inline-block';
       } else if (response['game_state'] === 'OVER') {
         sgf_down.style.display = 'inline-block';
         sgf_up.style.display = 'none';
         pass.style.display = 'none';
         undo.style.display = 'none';
         resign.style.display = 'none';
       } else {
         pass.style.display = 'none';
         undo.style.display = 'none';
         resign.style.display = 'none';
         sgf_down.style.display = 'none';
         sgf_up.style.display = 'none';
       }
     }
  }
  xhr.open('POST', url, true);
  xhr.responseType = 'json'; // parse the resonse body as JSON

  // "I am sending you some Javascript (JSON) in the body"
  xhr.setRequestHeader('Content-Type', 'application/json');

  // "Please reply in the JSON language, not HTML"
  xhr.setRequestHeader('Accept', 'application/json');

  xhr.send(data);
}
