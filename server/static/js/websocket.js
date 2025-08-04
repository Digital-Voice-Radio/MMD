// Create a new WebSocket connection to a server.
// Use 'wss://' for secure connections (recommended for production).
var socket = new WebSocket((location.protocol == "https:" ? "wss://" : "ws://") +location.host + "/ws");

// Event listener for when the connection is successfully established.
socket.onopen = (event) => {
  console.log('WebSocket connection opened:', event);
  socket.send('Hello Server!'); 
};

// Event listener for when a message is received from the server.
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
	console.log(data);
  if(data.state && data.extension) {
	  const el = document.getElementById('ext-' + data.exchange + '-' + data.extension)
	  if(el) {
		  console.log(el)
		  el.className = 'state-' + data.state;
	  }
  }
  console.log('Message from server:', event.data);
};

// Event listener for when the connection is closed.
socket.onclose = (event) => {
  console.log('WebSocket connection closed:', event.code, event.reason);
};

// Event listener for any errors that occur during the connection.
socket.onerror = (error) => {
  console.error('WebSocket error:', error);
};


