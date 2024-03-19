
function chut(container) {
  container.classList.toggle("active");
}

document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("search").addEventListener("input", function() {
      var searchTerm = this.value.trim().toLowerCase(); 
      var images = document.querySelectorAll(".img");
      var names = document.querySelectorAll(".image-name");
      images.forEach(function(image) {
          var filename = image.getAttribute("alt"); 
          if (filename.toLowerCase().includes(searchTerm)) {
              image.style.display = "inline-block"; 

          } else {
              image.style.display = "none"; 
          }
      });
      names.forEach(function(name) {
          var filename = name.innerHTML; 
          if (filename.toLowerCase().includes(searchTerm)) {
              name.style.display = "block"; 
          } else {
              name.style.display = "none"; 
          }
      });
  });
});

// window.location.reload();

document.addEventListener("DOMContentLoaded", function() {
 
  const loader = document.querySelector('#loader');
  loader.style.display = 'none';

  // Function to toggle the loader display
  function toggleLoader() 
  {
      if (loader.style.display === 'block') {
          loader.style.display = 'none';
      } else {
          loader.style.display = 'block';
      }
  }

  // Event listener for the click event to toggle the loader display
  const button = document.getElementById('qq'); // Replace 'yourButtonId' with the ID of your button
  button.addEventListener('click', function() {
      toggleLoader();
      // setTimeout(function() {
      //     // Once the video creation/loading is done, toggle the loader again to hide it
      //     toggleLoader();
      //     // Here you can display the video or perform any other action
      //     // For now, let's just log a message
      //     console.log('Video created/loaded successfully!');
      // }, 10000); // Simulate a delay of 3 seconds (3000 milliseconds)
  });
});
