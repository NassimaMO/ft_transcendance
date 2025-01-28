document.querySelectorAll('.display-button').forEach(function(button) {
  button.addEventListener('click', function() {

    var contentToHide = document.querySelector('.statistics');
    var otherContentToHide = document.querySelector('.streak');
    var infoContentToHide = document.querySelector('.more-info');
    var newContent = document.querySelector('.overlay-info');

    contentToHide.style.display = contentToHide.style.display === "none" ? "flex" : "none";
    otherContentToHide.style.display = otherContentToHide.style.display === "none" ? "block" : "none";
    newContent.style.display = newContent.style.display === "block" ? "none" : "block";
    infoContentToHide.style.display = infoContentToHide.style.display === "none" ? "block" : "none";
  });
});