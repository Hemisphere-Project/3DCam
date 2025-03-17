const WIDTH = 640;
const HEIGHT = 480;
const SCALE = 1;

const BIG_WIDTH = WIDTH * SCALE;
const BIG_HEIGHT = HEIGHT * SCALE;

var canvasRaw = document.getElementById("canRaw"),
    ctxRaw = canvasRaw.getContext("2d");

canvasRaw.width = BIG_WIDTH;
canvasRaw.height = BIG_HEIGHT;

var canvasProc = document.getElementById("canProc"),
    ctxProc = canvasProc.getContext("2d");

canvasProc.width = BIG_WIDTH;
canvasProc.height = BIG_HEIGHT;


// connect to the server using socketio
var socket = io.connect();

// on socket connection
socket.on('connect', () => {
    console.log('Connected!');
    socket.emit('join', 'BLOBS')
    socket.emit('join', 'VISU-RAW')
    socket.emit('join', 'VISU-PROC')
})

// on socket disconnection
socket.on('disconnect', () => {
    console.log('Disconnected!');
})

// on socket error
socket.on('error', () => {
    console.log('Error!');
})

socket.on('3Dcam-BLOBS', (data) => {
    // console.log('3Dcam-BLOBS', data);
    document.getElementById('blobs').innerHTML = JSON.stringify(data, null, 2);
})

// on '3Dcam-VISU-RAW'
socket.on('3Dcam-VISU-PROC', (data) => {
  data = new Uint8Array(data)

  // size of data
  console.log(data.length)

  const arrayBuffer = new ArrayBuffer(BIG_WIDTH * BIG_HEIGHT * 4);
  const pixels = new Uint8ClampedArray(arrayBuffer);

  // data is 3 channels only, convert to 4 channels
  for (let y = 0; y < BIG_WIDTH; y++) {
    for (let x = 0; x < BIG_HEIGHT; x++) {
      const k = (y*BIG_HEIGHT + x);
      const i = k * 4;
      pixels[i  ] = data[k*3]   // red
      pixels[i+1] = data[k*3+1] // green
      pixels[i+2] = data[k*3+2] // blue
      pixels[i+3] = 255         // alpha
    }
  }
  

  const imageData = new ImageData(pixels, BIG_WIDTH, BIG_HEIGHT);
  ctxProc.putImageData( imageData, 0, 0);
})



// on '3Dcam-VISU-RAW'
socket.on('3Dcam-VISU-RAW', (data) => {
  data = new Uint8Array(data)

  const arrayBuffer = new ArrayBuffer(WIDTH * HEIGHT * 4);
  const pixels = new Uint8ClampedArray(arrayBuffer);
  for (let y = 0; y < HEIGHT; y++) {
    for (let x = 0; x < WIDTH; x++) {
      const k = (y*WIDTH + x);
      const i = k * 4;
      let d = 255-data[k]
      pixels[i  ] = d   // red
      pixels[i+1] = d   // green
      pixels[i+2] = d   // blue
      pixels[i+3] = 255 // alpha
    }
  }

  const imageData = new ImageData(pixels, WIDTH, HEIGHT);
  ctxRaw.putImageData( scaleImageData(imageData, SCALE), 0, 0);
})


function scaleImageData(imageData, scale) 
{
  if (scale == 1) return imageData;
  
  var scaled = ctxRaw.createImageData(imageData.width * scale, imageData.height * scale);
  var subLine = ctxRaw.createImageData(scale, 1).data
  for (var row = 0; row < imageData.height; row++) {
      for (var col = 0; col < imageData.width; col++) {
          var sourcePixel = imageData.data.subarray(
              (row * imageData.width + col) * 4,
              (row * imageData.width + col) * 4 + 4
          );
          for (var x = 0; x < scale; x++) subLine.set(sourcePixel, x*4)
          for (var y = 0; y < scale; y++) {
              var destRow = row * scale + y;
              var destCol = col * scale;
              scaled.data.set(subLine, (destRow * scaled.width + destCol) * 4)
          }
      }
  }
  return scaled;
}

// Fill Conf
socket.on('3Dcam-CONF', (data) => {
  // clear conf id
  document.getElementById('conf').innerHTML = '';

  // foreach conf: append key as label, then input number for value or values
  for (const [key, value] of Object.entries(data)) {

    let confBox = document.createElement('div');
    confBox.setAttribute('class', 'confBox');
    document.getElementById('conf').appendChild(confBox);

    // console.log(`${key}: ${value}`);
    let label = document.createElement('label');
    label.setAttribute('for', key);
    label.innerHTML = key;
    confBox.appendChild(label);

    if (typeof value === 'number') {
      let input = document.createElement('input');
      input.setAttribute('type', 'number');
      input.setAttribute('id', key);
      input.setAttribute('name', key);
      input.setAttribute('value', value);
      confBox.appendChild(input);
      input.onchange = sendConf
    } else {
      for (const [i, v] of value.entries()) {
        if (typeof v === 'number') {
          let input = document.createElement('input');
          input.setAttribute('type', 'number');
          input.setAttribute('id', key + i);
          input.setAttribute('name', `${key}[${i}]`);
          input.setAttribute('value', v);
          confBox.appendChild(input);
          input.onchange = sendConf
        }
        else {
          for (const [j, v2] of v.entries()) {
            let input = document.createElement('input');
            input.setAttribute('type', 'number');
            input.setAttribute('id', key + i + j);
            input.setAttribute('name', `${key}[${i}][${j}]`);
            input.setAttribute('value', v2);
            confBox.appendChild(input);
            input.onchange = sendConf
          }
        }
      }
    }
  }
})

function sendConf() {
  let data = {}
  let inputs = document.getElementsByTagName('input')
  for (let i = 0; i < inputs.length; i++) {
    // use input name 
    let name = inputs[i].name
    let value = parseFloat(inputs[i].value)
    
    let keys = name.split(/[\[\]]+/)

    // remove empty strings
    keys = keys.filter(function(e) { return e !== '' })

    // remove first element
    mkey = keys.shift()

    // direct value
    if (keys.length == 0) {
      data[mkey] = value
    }

    // build multi dimensional array in data[mkey]
    else {
      if (!(mkey in data)) data[mkey] = []

      let warr = data[mkey]
      for (let j = 0; j < keys.length; j++) {
        let knum = parseInt(keys[j])
        if (j == keys.length - 1) {
          warr[knum] = value
        }
        else {
          if (!(knum in warr)) warr[knum] = []
          warr = warr[knum]
        }
      }
    }
  }
  socket.emit('3Dcam-CONF', data)
  // console.log(data)
}
  