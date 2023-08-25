let form = document.getElementById('lobby__form')
let videoCall = document.getElementById('video_call_btn')

var scriptElement = document.currentScript;
var roomid = scriptElement.getAttribute('data-room-id');
console.log(roomid)

let displayName = sessionStorage.getItem('display_name')
let hostId = sessionStorage.getItem('uid')

const csrftoken = getCookie('csrftoken');
if(displayName){
    form.name.value = displayName
}

// document.addEventListener('DOMContentLoaded', onPageLoad);
// function onPageLoad() {
//   changeVideoCallStatus(roomid)
//   }



form.addEventListener('submit', (e) => {
    e.preventDefault()

    sessionStorage.setItem('display_name', e.target.name.value)
    sessionStorage.setItem('uid', e.target.hostId.value)
    sessionStorage.setItem('roomId', e.target.room.value)
    let inviteCode = e.target.room.value
    if(!inviteCode){
        inviteCode = String(Math.floor(Math.random() * 10000))
    }
    const data = {
        roomId : inviteCode,
        hostId : e.target.hostId.value
      };
  
    var dynamicURL = "/chat-room/" + inviteCode + "/";
    console.log(dynamicURL);
     window.open(dynamicURL, "_blank");
})


  // Function to retrieve the CSRF token from cookies
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }
  

 // to scroll downward

 // Get the message box element
const messageBox = document.getElementById('message-box');


// Scroll to the bottom of the message box
messageBox.scrollTop = messageBox.scrollHeight;

// Get the necessary elements
const fileInput = document.getElementById('upload');
const previewDiv = document.getElementById('preview');
const fileNameSpan = document.getElementById('file-name');
const removeButton = document.getElementById('remove-button');

// Add event listener for file input change
fileInput.addEventListener('change', handleFileUpload);

// Function to handle file upload
function handleFileUpload() {
  const file = fileInput.files[0];
  if (file) {
    // Show the preview div
    previewDiv.classList.add('show');

    // Display the file name
    fileNameSpan.textContent = file.name;
  }

}

// Add event listener for remove button click
removeButton.addEventListener('click', removeFile);

// Function to remove the file and hide the preview div
function removeFile() {
  // Clear the file input
  fileInput.value = '';

  // Hide the preview div
  previewDiv.classList.remove('show');
}

function makeUrlsClickable() {
  const msgTextElements = document.getElementsByClassName('msg_text');

  for (let i = 0; i < msgTextElements.length; i++) {
    const msgText = msgTextElements[i].innerHTML;
    const urlRegex = /(https?:\/\/[^\s]+)/g; // Regular expression to match URLs
    const usernameRegex = /@(\w+)/g;

    // Replace URLs with clickable anchor tags
    const modifiedText = msgText.replace(urlRegex, function (url) {
      return '<a href="' + url + '">' + url + '</a>';
    });

    const messageWithClickableUsernames = modifiedText.replace(usernameRegex, (match, username) => {
      return `<a href="/user/profile/${roomid}/${username}" >@${username}</a>`;
    });

    // Update the content of the div with clickable URLs
    msgTextElements[i].innerHTML = messageWithClickableUsernames;
  }
 
}

// Call the function to make URLs clickable
makeUrlsClickable();








