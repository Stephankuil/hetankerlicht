<script>
  document.addEventListener("DOMContentLoaded", function() {
    const bgUrl = "{{ url_for('static', filename='uploads/ocean_landscape.jpg') }}";
    document.body.style.setProperty('--bg-image', `url(${bgUrl})`);
    document.querySelector("body::before"); // ensure selector works
    const style = document.createElement('style');
    style.innerHTML = `
      body::before {
        background-image: url(${bgUrl});
        background-repeat: no-repeat;
        background-position: center center;
        background-attachment: fixed;
      }
    `;
    document.head.appendChild(style);
  });
</script>