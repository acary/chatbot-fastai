function submit_message() {

  var name = document.getElementById("name");
  var message = document.getElementById("message");
  var sent_msg = document.getElementById("sent_msg");

  var entry = {
    name: name.value,
    message: message.value
  };

  sent_msg.innerText = entry.message;

  fetch(`${window.origin}/create-entry`, {
      method: "POST",
      credentials: "include",
      body: JSON.stringify(entry),
      cache: "no-cache",
      headers: new Headers({
        "content-type": "application/json"
      })
    })
    .then(function(response) {
      if (response.status !== 200) {
        console.log(`Looks like there was a problem. Status code: ${response.status}`);
        return;
      }
      response.json().then(function(data) {
        console.log(data.result);
        document.getElementById('message').value = '';
        document.getElementById('messages').innerText = data.result;
      });
    })
    .catch(function(error) {
      console.log("Fetch error: " + error);
    });
}
