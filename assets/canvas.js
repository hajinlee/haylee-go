var myCanvas = document.getElementById('test');
var ctx = myCanvas.getContext('2d');

//myCanvas.style.position = 'absolute';
//myCanvas.style.left = '50px';
//myCanvas.style.top = '50px';

function board_js() {
  var board_js = [];
  for (let i=0; i<19; i++) {
    board_js.push("+++++++++++++++++++");
  }
  return board_js;
}

var cell_width = 24;
var cell_height = 26;
var margin = 15;

var board_size = 18;
var board_width = (cell_width * board_size) + (margin * 2);
var board_height = (cell_height * board_size) + (margin * 2);

myCanvas.width = board_width;
myCanvas.height = board_height;

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
}
myCanvas.addEventListener('click', onMouseClick, true);

ctx.fillStyle = 'AntiqueWhite';
ctx.fillRect( 0, 0, board_width, board_height );

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

function starPoint(x_pos, y_pos) {
  ctx.beginPath();
  ctx.arc(x_pos,y_pos,5,0,2*Math.PI);
  ctx.fill();
}

for (let x=(cell_width*3)+margin; x<=(cell_width*15)+margin; x+=cell_width*6){
  starPoint(x, 93);
  starPoint(x, 249);
  starPoint(x, 405);
}

function addStone(color, x, y) {
  let pos = coordToPixel(x, y);

  ctx.beginPath();
  ctx.arc(pos.x,pos.y,11,0,2*Math.PI);
  ctx.stroke();
  ctx.fillStyle = color;
  ctx.fill();
}

function updateBoard() {
  for (let i=0; i<19; i++) {
    for (let j=0; j<19; j++) {
      if (board_js[i][j] == '@') {
        addStone('black', j, i)
      }
      else if (board_js[i][j] == 'O') {
        addStone('white', j, i)
      }
    }
  }
}

myboard = board_js()
myboard[2][3] = "@"
myboard[16][16] = "O"
updateBoard()

addStone('black', 2, 3);
