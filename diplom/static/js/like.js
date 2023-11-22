document.addEventListener('DOMContentLoaded', function() {
    var likeButtons = document.querySelectorAll('.like-button');

    likeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var projectId = this.dataset.projectId;

            var csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;

            var formData = new FormData();
            formData.append('csrfmiddlewaretoken', csrf_token);

            fetch(`/like_project/${projectId}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                var likeCountElement = button.nextElementSibling;
                var likeCount = parseInt(likeCountElement.innerText);

                if (data.liked) {
                    likeCount++;
                } else {
                    likeCount--;
                }

                likeCountElement.innerText = likeCount;
            });
        });
    });
});
