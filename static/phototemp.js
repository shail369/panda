const selectedImages = [];

// Retrieve selected images from localStorage
var photoq = localStorage.getItem('id');
selectedImages.push(...JSON.parse(photoq) || []); // Push parsed items to the selectedImages array or initialize an empty array if null

function chut(container) {
    container.classList.toggle("active");
}

function chints(id) {   
    var storedIds = JSON.parse(localStorage.getItem('id')) || []; // Retrieve stored ids or initialize an empty array
    
    var index = storedIds.indexOf(id);
    
    if (index !== -1) {
        storedIds.splice(index, 1);
    } else {
        storedIds.push(id);
    }
    
    localStorage.setItem('id', JSON.stringify(storedIds));
}

// Assuming you have a form with the id "imageForm"
const form = document.getElementById('imageForm');

// Listen for form submissions
form.addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission
    
    const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');

    checkboxes.forEach(function(checkbox) {
        selectedImages.push(checkbox.value);
    });

    // Update localStorage with the selected images
    localStorage.setItem('id', JSON.stringify(selectedImages));
});
