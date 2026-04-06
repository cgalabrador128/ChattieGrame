$(function() {
    $('#profile_button').on('click', function(e) {
    e.preventDefault()
    $.getJSON('/d_Func/profile_upload',
        function(data) {
        //do nothing
    });
    return false;
    });
});

$(function() {
    $('.add-member-button').on('click', function(e) {
    e.preventDefault()
    $.getJSON('/d_Func/add_member_button',
        function(data) {
        //do nothing
    });
    return false;
    });
});

async function uploadImage() {
      const fileInput = document.getElementById("fileInput");
      const file = fileInput.files[0];

      if (!file) {
        alert("Please select an image.");
        return;
      }

      const formData = new FormData();
      formData.append("file", file);

      document.getElementById("status").textContent = "Uploading...";

      const res = await fetch("/d_Func/profile_upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (res.ok) {
        document.getElementById("status").textContent = "Upload successful!";
        document.getElementById("preview").src = data.url;
        document.getElementById("preview").style.display = "block";
      } else {
        document.getElementById("status").textContent = "Error: " + data.error;
      }
    }