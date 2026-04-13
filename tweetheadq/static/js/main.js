document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("searchInput");
    const resultsBox = document.getElementById("searchResults");

    let timeout = null;

    input.addEventListener("keyup", function () {
        const query = input.value.trim();

        clearTimeout(timeout);

        if (query.length < 2) {
            resultsBox.classList.add("d-none");
            resultsBox.innerHTML = "";
            return;
        }

        timeout = setTimeout(() => {
            fetch(`/search-users/?q=${query}`)
                .then(res => res.json())
                .then(data => {

                    resultsBox.innerHTML = "";

                    if (data.results.length === 0) {
                        resultsBox.innerHTML = `
                            <div class="list-group-item text-muted">
                                No users found
                            </div>
                        `;
                    } else {
                        data.results.forEach(user => {

                            const item = document.createElement("a");
                            item.classList.add("list-group-item", "list-group-item-action");

                            item.textContent = user.username;
                            item.href = `/profile/${user.id}/`;

                            resultsBox.appendChild(item);
                        });
                    }

                    resultsBox.classList.remove("d-none");
                })
                .catch(error => {
                    console.error("Search error:", error);
                });
        }, 300);
    });

    // Hide dropdown on outside click
    document.addEventListener("click", function (e) {
        if (!input.contains(e.target) && !resultsBox.contains(e.target)) {
            resultsBox.classList.add("d-none");
        }
    });

});

// Existing functions (cleaned)
function toggleComments(tweetId) {
    const section = document.getElementById(`comments-${tweetId}`);
    section.style.display = section.style.display === "block" ? "none" : "block";
}

function toggleEdit(commentId) {
    const view = document.getElementById(`comment-view-${commentId}`);
    const edit = document.getElementById(`comment-edit-${commentId}`);

    if (edit.style.display === "none") {
        edit.style.display = "block";
        view.style.display = "none";
    } else {
        edit.style.display = "none";
        view.style.display = "block";
    }
}