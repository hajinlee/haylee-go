var myCanvas = document.getElementById('test');
var ctx = myCanvas.getContext('2d');

// Fixing the go board position if necessary
//myCanvas.style.position = 'absolute';
//myCanvas.style.left = '50px';
//myCanvas.style.top = '50px';

var cell_width = 24;
var cell_height = 26;
var margin = 15;

var board_size = 18;
var board_width = (cell_width * board_size) + (margin * 2);
var board_height = (cell_height * board_size) + (margin * 2);

myCanvas.width = board_width;
myCanvas.height = board_height;

// if any stones are on the board, this is an array of strings,
// one per row, like '+++@@OO+++'
var stone_positions = null;

// start loading the background image
var background = new Image();
background.src = "assets/kaya.jpg";

var white_stone = new Image();
white_stone.src = "assets/white.png";

var black_stone = new Image();
black_stone.src = "assets/black.png"

// after the background image finishes loading, redraw the board
background.addEventListener('load', function(event) { drawBoard(); }, true);
white_stone.addEventListener('load', function(event) { drawBoard(); }, true);
black_stone.addEventListener('load', function(event) { drawBoard(); }, true);

function coordToPixel(x, y) {
  let x_pos = (x * cell_width) + margin;
  let y_pos = (y * cell_height) + margin;
  return { x: x_pos, y: y_pos };
}

function pixelToCoord(x, y) {
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
  var pos = pixelToCoord(offsetX, offsetY);
  console.log(offsetX, offsetY, pos.x, pos.y);

  var rbox = document.getElementById('remove');
  if (rbox) {
    rbox.value = rbox.value + ' ' + pos.y.toFixed(0) + ',' + pos.x.toFixed(0);
  }
  else {
    clickToSubmit(pos.y, pos.x);
  }
}

function starPoint(x_pos, y_pos) {
  ctx.beginPath();
  ctx.arc(x_pos,y_pos,5,0,2*Math.PI);
  ctx.fill();
}

function drawStone(color, x, y) {
  let pos = coordToPixel(x, y);
  var img = color == 'white' ? white_stone : black_stone;
  ctx.drawImage(img, pos.x - 11, pos.y - 11, 22, 22);
}

/* Draw stone using an arc:
ctx.beginPath();
ctx.arc(pos.x,pos.y,11,0,2*Math.PI);
ctx.stroke();
ctx.fillStyle = color;
ctx.fill();
*/

myCanvas.addEventListener('click', onMouseClick, true);

// whenever the window resizes, redraw the board
window.addEventListener('resize', function(event) { drawBoard(); }, true);

function clickToSubmit(x, y) {
  var xbox = document.getElementById('xcoord');
  xbox.value = x.toFixed(0);
  var ybox = document.getElementById('ycoord');
  ybox.value = y.toFixed(0);
  var submit_button = document.getElementById('submit');
  submit_button.click();
}

function clickToSelect(x, y) {
  var rbox = document.getElementById('remove');
  rbox.value = rbox.value += x.toFixed(0) + ',' + y.toFixed(0) + ' ';

}

function drawBoard() {
  // draw the wood board background image
  if(background.complete /* && white_stone.complete && black_stone.complete */) {
    // all the images are loaded now

    // draw the background
    ctx.drawImage( background, 0, 0, board_width, board_height );
  } else {
    // the image has not finished downloading yet.
    // stop here. We will try to draw again when the image finishes,
    // in the "load" event handler.
    return; // don't draw a white board

    // (just in case the board needs a white background:)
    // ctx.beginPath();
    // ctx.rect(0, 0, board_width, board_height);
    // ctx.fillStyle = '#ffffff';
    // ctx.fill();
  }

  // Draw vertical lines on the board.
  for (let x=margin; x<=board_height-margin; x+=cell_height){
    ctx.strokeStyle = '#000000';
    ctx.beginPath();
    ctx.moveTo( margin, x );
    ctx.lineTo( board_width-margin, x );
    ctx.closePath();
    ctx.lineWidth = 1;
    ctx.fillStyle = '#000000';
    ctx.stroke();
  }

  // Draw horizontal lines on the board.
  for (let x=margin; x<=board_width-margin; x+=cell_width){
    ctx.strokeStyle = '#000000';
    ctx.beginPath();
    ctx.moveTo( x, margin );
    ctx.lineTo( x, board_height-margin );
    ctx.closePath();
    ctx.lineWidth = 1;
    ctx.fillStyle = '#000000';
    ctx.stroke();
  }

  for (let x=(cell_width*3)+margin; x<=(cell_width*15)+margin; x+=cell_width*6){
    starPoint(x, 93);
    starPoint(x, 249);
    starPoint(x, 405);
  }

  if(stone_positions) {
    for (let i=0; i<19; i++) {
      for (let j=0; j<19; j++) {
        if (stone_positions[i][j] == '@') {
          drawStone('black', j, i)
        }
        else if (stone_positions[i][j] == 'O') {
          drawStone('white', j, i)
        }
      }
    }
  }
}

// update the stone positions.
// given a list of strings like ["+++@++", ...]
function updateBoard(board_js) {
  // update the stone positions.
  stone_positions = [];
  for(let i = 0; i < 19; i++) {
    stone_positions.push(board_js[i]);
  }
  // redraw the board
  drawBoard();
}