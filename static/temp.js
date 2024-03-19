function chut(container) {
    container.classList.toggle("active");
  }
  
  const myVideo = document.getElementById("video2");
  const length = document.getElementById("duration");
  
  // Check if the input field is empty
  
  
  function playPause() { 
      if (myVideo.paused) 
        myVideo.play(); 
      else 
        myVideo.pause(); 
    } 
  
  function starting() {
      myVideo.currentTime = 0;
      myVideo.pause();
  }
  
  // document.getElementsByClassName("musicselect").addEventListener("change", function() {
  //   var selectedMusic = this.value;
  //   var xhr = new XMLHttpRequest();
  //   xhr.open("POST", "/audio", true);
  //   xhr.setRequestHeader("Content-Type", "application/json");
  //   xhr.onreadystatechange = function () {
  //       if (xhr.readyState === 4 && xhr.status === 200) {
  //           var response = JSON.parse(xhr.responseText);
  //           myVideo.src = response.video_path + '?nocache=' + new Date().getTime();
  //           myVideo.load();
  //           starting();
  //       }
  //   };
  //   xhr.send(JSON.stringify({ music: selectedMusic}));
  // });
  
  function duration() {
    if (!length.value.trim())
   {
      length.value = 2;
   }
  
    var duration = length.value;
  
    var selectedImages = [];
    var selectedMusic = [];
    var checkboxes = document.querySelectorAll('input[name="selectedImages"]:checked');
    checkboxes.forEach(function(checkbox) {
        selectedImages.push(checkbox.value);
    });
    var imageboxes = document.querySelectorAll('input[name="selectedMusic"]:checked');
    imageboxes.forEach(function(checkbox) {
        selectedMusic.push(checkbox.value);
    });
    
    
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/duration", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            myVideo.src = response.video_path + '?nocache=' + new Date().getTime();
            myVideo.load();
            starting();
        }
    };
    console.log("duration", duration);
    var transition = document.getElementById("transition").value;
    // Include duration and selected images in the request
    xhr.send(JSON.stringify({ duration: duration, selectedImages: selectedImages, selectedMusic: selectedMusic , transition : transition }));4
    length.value = "";
  }
  
  function resizeVideo() {
    var selectedResolution = document.getElementById("resolutionSelect").value;
    var formData = new FormData();
    formData.append("selectedResolution", selectedResolution);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/resize_video", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            setTimeout(3000);
            var response = JSON.parse(xhr.responseText);
            myVideo.src = response.video_path + '?nocache=' + new Date().getTime();
            myVideo.load();
            starting();
        }
    };
    xhr.send(JSON.stringify({ selectedResolution: selectedResolution }));
  }