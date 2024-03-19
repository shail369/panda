var flag = 0;
var flag1 = 0;
var flag3 = 0;
document.getElementById("imageInput").addEventListener("change", previewImages);
document
  .getElementById("dropContainer")
  .addEventListener("dragover", allowDrop);
document.getElementById("dropContainer").addEventListener("drop", handleDrop);

var existingFiles = [];

function previewImages() {
  flag = 0;
  flag1 = 1;
  var previewContainer = document.getElementById("imagePreview");
  var existingImages = document.querySelectorAll(".image-container");
  var files = Array.from(document.getElementById("imageInput").files);
  var dataTransfer = new DataTransfer();
  existingFiles.forEach(function(file) {
    dataTransfer.items.add(file);
  });
  files.forEach(function(file) {
    dataTransfer.items.add(file);
  });
  document.getElementById("imageInput").files = dataTransfer.files;
  existingFiles = Array.from(document.getElementById("imageInput").files);
  files.forEach(function (file) {
    processFile(file);
  });
  updateChosenImages();
}

function allowDrop(event) {
  // flag=1;
  event.preventDefault();
  flag = 0;
  flag1 = 0;
  flag3 = 0;
}

function handleDrop(event) {
  event.preventDefault();
  if( flag3 == 0)
  {
  var newFiles = event.dataTransfer.files;
  
  var allFiles = existingFiles.concat(Array.from(newFiles));

  var dataTransfer = new DataTransfer();
  allFiles.forEach(function(file) {
    dataTransfer.items.add(file);
  });
  
  document.getElementById("imageInput").files = dataTransfer.files;
  existingFiles = Array.from(document.getElementById("imageInput").files);
  flag3 = 1;
  }
  Array.from(newFiles).forEach(function (file) {
    processFile(file);
  });

}

function processFile(file) {
  var a = document.getElementById("imageInput");
      console.log(a.files);
  var reader = new FileReader();
  var a = document.getElementById("imageInput");
      console.log(a.files);
  reader.onload = function (e) {
    if (flag1 == 1) {
      var imageContainer = document.createElement("div");
      imageContainer.classList.add("image-container");
      var images = document.getElementById("imageInput");
      var image = document.createElement("img");
      image.src = e.target.result;
      var a = document.getElementById("imageInput");
      console.log(a.files);
      var closeButton = document.createElement("span");
      closeButton.innerHTML = "&times;";
      closeButton.classList.add("close-icon");

      closeButton.addEventListener("click", function () {
        var indexToRemove = Array.from(
          imageContainer.parentNode.children
        ).indexOf(imageContainer);
        imageContainer.remove();
        var newFiles = Array.from(images.files);
        newFiles.splice(indexToRemove, 1);
        var filesList = new DataTransfer();
        newFiles.forEach(function (file) {
          filesList.items.add(file);
        });
        images.files = filesList.files;
        updateChosenImages();
      });
      var a = document.getElementById("imageInput");
      console.log(a.files);
      imageContainer.appendChild(image);
      imageContainer.appendChild(closeButton);

      document.getElementById("imagePreview").appendChild(imageContainer);
      updateChosenImages();
    } else if (flag % 2 == 0) {
      var imageContainer = document.createElement("div");
      imageContainer.classList.add("image-container");
      var images = document.getElementById("imageInput");
      var image = document.createElement("img");
      image.src = e.target.result;
      var a = document.getElementById("imageInput");
      console.log(a.files);
      var closeButton = document.createElement("span");
      closeButton.innerHTML = "&times;";
      closeButton.classList.add("close-icon");

    //   closeButton.addEventListener("click", function () {
    //     var indexToRemove = Array.from(imageContainer.parentNode.children).indexOf(imageContainer);
    //     console.log(indexToRemove);
    //     var index = Array.from(imageContainer.parentNode.children);
    //     var newFiles = Array.from(images);
    //     for (var i = 0; i < newFiles.length; i++) {
    //         if (i == indexToRemove) {
    //         }
    //         else {
    //             newFiles.splice(i, 1);
    //             console.log(i,newFiles.length);
    //         }
    //     }
    //     imageContainer.remove();
    //     updateChosenImages();

        // var filesList = new DataTransfer();
        // filteredFiles.forEach(function (file) {
        //   filesList.items.add(file);
        // });
    //  });

      imageContainer.appendChild(image);
      imageContainer.appendChild(closeButton);
      var a = document.getElementById("imageInput");
      console.log(a.files);
      document.getElementById("imagePreview").appendChild(imageContainer);
      updateChosenImages();
    }
    flag++;
  };
  var a = document.getElementById("imageInput");
      console.log(a.files);
  reader.readAsDataURL(file);
}

function dikha()
{
  var a = document.getElementById("imageInput");
  console.log(a.files);
  console.log(existingFiles);
}

function updateChosenImages() {
  var chosenImagesCount = document.querySelectorAll(".image-container").length;
  var countLabel = document.getElementById("chosenImagesCount");
  countLabel.textContent = "Chosen Images: " + chosenImagesCount;
  var a = document.getElementById("imageInput");
      console.log(a.files);
}

function uploadImages() {
  var formData = new FormData(document.getElementById("imageForm"));

  console.log(formData.getAll("file"));
}

function clearAllImages() {
  var images = document.getElementById("imageInput");
  images.remove();
  var previewContainer = document.getElementById("imagePreview");
  previewContainer.innerHTML = "";
  updateChosenImages();
}

