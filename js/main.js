const note_div = document.querySelector('#note_div')

function startTimer() {
  const microseconds = 2000  // 2 seconds
  window.setTimeout(fetchCurrentNote, microseconds)
}

function fetchCurrentNote() {
  fetch('/ajax/get_current_node')
    .then(function(response) {
      return response.json()
    })
    .then(function (myJson) {
      // Update the div.
      note_div.innerHTML = myJson.note

      // Start the timer for the next request
      startTimer()
    })
}

if (note_div != null) {
  // If note_div is null it means that the user is not logged in.  This is
  // because the jinja template for the '/' handler only renders this div
  // when the user is logged in.  Querying for a node that does not exist
  // returns null.

  fetchCurrentNote()
}
