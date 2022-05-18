let errorText = 'Something went wrong...';
let wordleTemplate = (url, displayUrl, likes, isFavorite, isLiked, dataIndex) => {
    return `
    <div id="${'wordle' + data[dataIndex].id}" class="wordle">
        <a href="${url}" target="_blank" class="clickable"><p>${displayUrl}</p></a>
        <div class="grow"></div>
        <button onclick="openInfo(${dataIndex});" class="icon-info-circled clickable"></button>
        <button onclick="toggleFavorite(${dataIndex});" class="${'icon-star' + (isFavorite ? '' : '-empty')}" clickable"></button>
        <button onclick="toggleLike(${dataIndex});" class="${'icon-thumbs-up' + (isLiked ? '-alt' : '')} clickable"></button>
        <p class="likes">${likes}</p>
    </div>`
};
let dividerElement = `<hr class="divider">`;

let storage = false;
let favoriteSet = new Set();
let likeSet = new Set();
if (typeof(localStorage) !== "undefined") {
    storage = true;
    if (localStorage.getItem("favorites") == null) {
        localStorage.setItem("favorites", JSON.stringify(Array.from(favoriteSet)));
    } else {
        favoriteSet = new Set(JSON.parse(localStorage.getItem("favorites")));
    }
    if (localStorage.getItem("likes") == null) {
        localStorage.setItem("likes", JSON.stringify(Array.from(likeSet)));
    } else {
        likeSet = new Set(JSON.parse(localStorage.getItem("likes")));
    }
}

function updateStorage() {
    if (storage) {
        localStorage.setItem("favorites", JSON.stringify(Array.from(favoriteSet)));
        localStorage.setItem("likes", JSON.stringify(Array.from(likeSet)));
    }
}

function handleErrors(response) {
    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}

let pageLoaded = false;
let dataLoaded = false;
let data = null;
fetch("/api/wordles").then(handleErrors).then(response => response.json()).then(json => {
    data = [];
    for (i in json) {
        let obj = json[i];
        let parts = obj.url.split('/');
        data.push({
            id: obj.id,
            url: obj.url,
            displayUrl: parts.slice(2).join('/'),
            data: obj.data,
            date: obj.date,
            likes: obj.likes,
            isLiked: likeSet.has(obj.id),
            isFavorite: favoriteSet.has(obj.id)
        });
    }
    dataLoaded = true;
    update();
}).catch(error => {
    dataLoaded = true;
    update();
    console.error("Failed to fetch Wordles:\n" + error);
});

let likesLoaded = false;
let serverLikes = new Set();
fetch("/api/likes").then(handleErrors).then(response => response.json()).then(json => {
    serverLikes = new Set(json);
    likeSet = new Set([...serverLikes, ...likeSet]);
    updateStorage();
    likesLoaded = true;
    update();
}).catch(error => {
    console.error("Failed to fetch liked Wordles:\n" + error);
});

window.onload = function() {
    wordles = document.getElementById("wordles");
    search = document.getElementById("search");
    favorites = document.getElementById("favorites");
    sort = document.getElementById("sort");
    direction = document.getElementById("sortDirection");
    sortDirection = 0;
    pageLoaded = true;
    setupInfoModal();
    update();
}

function setupInfoModal() {
    modal = document.getElementById("infoModal");
    modalUrl = document.getElementById("modalUrl");
    modalData = document.getElementById("modalData");
    modalDate = document.getElementById("modalDate");
    modalLikes = document.getElementById("modalLikes");
    let span = document.getElementById("modalClose");
    span.onclick = function() {
        modal.style.display = "none";
    };
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };
}

function swapSort() {
    if (sortDirection == 1) {
        direction.innerHTML = "▼";
    } else {
        direction.innerHTML = "▲";
    }
    sortDirection = 1 - sortDirection;
    update();
}

function openInfo(dataIndex) {
    let wordle = data[dataIndex];
    modal.style.display = "block";
    modalUrl.innerText = wordle.url;
    modalData.innerText = wordle.data;
    modalDate.innerText = wordle.date;
    modalLikes.innerText = wordle.likes;
}

function toggleFavorite(dataIndex) {
    let id = data[dataIndex].id;
    if (favoriteSet.has(id)) {
        favoriteSet.delete(id);
        data[dataIndex].isFavorite = false;
    } else {
        favoriteSet.add(id);
        data[dataIndex].isFavorite = true;
    }
    let classes = document.getElementById("wordle" + id).children[3].classList;
    classes.toggle("icon-star");
    classes.toggle("icon-star-empty");
    updateStorage();
}

function updateWordleLikes(dataIndex, increment) {
    let id = data[dataIndex].id;
    let wordle = document.getElementById("wordle" + id);
    let classes = wordle.children[4].classList;
    classes.toggle("icon-thumbs-up");
    classes.toggle("icon-thumbs-up-alt");
    let p = wordle.children[5];
    p.innerText = parseInt(p.innerText) + increment;
    data[dataIndex].likes += increment;
    data[dataIndex].isLiked = !data[dataIndex].isLiked;
    updateStorage();
}

function toggleLike(dataIndex) {
    let id = data[dataIndex].id;
    if (likeSet.has(id)) {
        if (serverLikes.has(id)) {
            fetch(`/api/like/${id}/remove`, {method: "DELETE"}).then(handleErrors).then(response => {
                likeSet.delete(id);
                serverLikes.delete(id);
                updateWordleLikes(dataIndex, -1);
            }).catch(error => {
                console.error(`Failed to remove like on Wordle ${id}:\n${error}`);
            });
        } else {
            likeSet.delete(id);
            updateWordleLikes(dataIndex, -1);
        }
    } else {
        fetch(`/api/like/${id}/add`, {method: "PUT"}).then(handleErrors).then(response => {
            likeSet.add(id);
            serverLikes.add(id);
            updateWordleLikes(dataIndex, 1);
        }).catch(error => {
            console.error(`Failed to like Wordle ${id}:\n${error}`);
        });
    }
}

function update() {
    if (pageLoaded && dataLoaded) {
        wordles.innerHTML = "";
        if (data == null) {
            let error = document.createElement('p');
            error.innerHTML = errorText;
            wordles.appendChild(error);
        } else {
            data.sort((a, b) => {
                if (sort.value === 'alphabet') {
                    return a.displayUrl.localeCompare(b.displayUrl);
                } else if (sort.value === 'like') {
                    return b.likes - a.likes;
                } else if (sort.value === 'new') {
                    return a.date - b.date;
                }
            });
            if (sortDirection == 1) {
                data.reverse();
            }
            if (favorites.checked) {
                data.sort((a, b) => {
                    if (a.isFavorite && !b.isFavorite) {
                        return -1;
                    } else if (!a.isFavorite && b.isFavorite) {
                        return 1;
                    } else {
                        return 0;
                    }
                });
            }
            let result = [];
            for (i in data) {
                let w = data[i];
                if ((w.url + w.data).includes(search.value)) {
                    w.dataIndex = i;
                    result.push(w);
                }
            }
            for (i in result) {
                let wordle = result[i];
                let element = getElementFromHTML(
                    wordleTemplate(wordle.url, wordle.displayUrl, wordle.likes, wordle.isFavorite, wordle.isLiked, wordle.dataIndex));
                wordles.appendChild(element);
                if (favorites.checked && wordle.isFavorite && i + 1 < result.length && !result[parseInt(i) + 1].isFavorite) {
                    wordles.appendChild(getElementFromHTML(dividerElement));
                }
            }
        }
    }
}

function getElementFromHTML(htmlString) {
    let div = document.createElement('div');
    div.innerHTML = htmlString.trim();
    return div.firstChild;
}