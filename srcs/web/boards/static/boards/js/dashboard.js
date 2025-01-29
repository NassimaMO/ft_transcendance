document.querySelectorAll('.display-button').forEach(function(button) {
  button.addEventListener('click', function() {
    var contentToHide = document.querySelector('.statistics');
    var otherContentToHide = document.querySelector('.streak');
    var infoContentToHide = document.querySelector('.more-info');
    var newContent = document.querySelector('.overlay-info');

    if (contentToHide.classList.contains('hidden')) {
      contentToHide.classList.remove('hidden');
      otherContentToHide.classList.remove('hidden');
      newContent.style.display = "none";
      infoContentToHide.style.display = "block";
      otherContentToHide.style.display = "block";
    } else {
      contentToHide.classList.add('hidden');
      otherContentToHide.classList.add('hidden');
      newContent.style.display = "block";
      infoContentToHide.style.display = "none";
      otherContentToHide.style.display = "none";
    }
  });
});