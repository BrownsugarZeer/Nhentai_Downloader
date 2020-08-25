async function getGalleryID() {
  // clear the preview first, then restart
  document.getElementById("contain").style.backgroundImage = "";
  document.getElementById("preview").style.backgroundImage = "";
  document.getElementById("loading").style.width = "0%";

  var checkbox = document.getElementById("download");
  var ids = document.getElementsByClassName("galleryID");
  if (checkbox.checked == true) {
    for (let i = 0; i < ids.length; i++) {
      if (ids[i].value.length == 6) {
        document.getElementsByClassName("queue")[0].textContent += ids[i].value + "\n";
        await eel.getIdsArray(ids[i].value)();
      }
      ids[i].value = "";
    }
    await eel.galleryDownload()();
  }
}

// In main.py "startdownload2()"
window.eel.expose(showDownloadInfo, "showDownloadInfo");
function showDownloadInfo(bookname, totalpage, author) {
  var info = document.getElementsByClassName("downloadinfo")[0];
  info.textContent = author + " ~~~ Page: " + totalpage + " ~~~ " + bookname;
}

// In main.py "startdownload2()"
window.eel.expose(coverPreview, "coverPreview");
function coverPreview(MangaCover, book) {
  var cover = "url(" + MangaCover + book + ".jpg)";
  document.getElementById("contain").style.backgroundImage = cover;
  document.getElementById("preview").style.backgroundImage = cover;
  document.getElementById("loading").style.width = "1.35%";
}

// In main.py "startdownload2()"
window.eel.expose(progressBar, "progressBar");
function progressBar(i, totalpage) {
  var percent = ((i / totalpage) * 100).toFixed(2);
  document.getElementById("loading").style.width = percent + "%";
}

// In main.py "startdownload2()"
window.eel.expose(DownloadFinished, "DownloadFinished");
function DownloadFinished(MangaCover, ctn, norepeat) {
  if (norepeat == "True") {
    addIdsLink(MangaCover, ctn);
    document.getElementsByClassName("finished")[0].textContent += ctn + "\n";
  }
  var queue = document.getElementsByClassName("queue")[0].textContent;
  queue = queue.substr(7);
  document.getElementsByClassName("queue")[0].textContent = queue;
}

// In main.py "startdownload2()"
window.eel.expose(TotalFinished, "TotalFinished");
function TotalFinished() {
  toggleDownload();
  document.getElementById("download").checked = false;
  document.getElementsByClassName("icon0")[0].style.cursor = "pointer";
}

// In main.py "startdownload2()"
window.eel.expose(showStatus, "showStatus");
function showStatus(book, bookStatus) {
  var info = document.getElementsByClassName("Status")[0];
  info.textContent += book + " - " + bookStatus + "\n";
}

function toggleDownload() {
  var ids = document.querySelectorAll('#galleryIDs input[type="text"]');
  for (let i = 0; i < ids.length; i++) {
    ids[i].disabled = !ids[i].disabled;
  }
  var Dbtn = document.getElementById("download");
  Dbtn.disabled = !Dbtn.disabled;
  document.getElementsByClassName("icon0")[0].style.cursor = "progress";
}

document.getElementById("Fbtn").addEventListener("click", toggleFbtn);
function toggleFbtn() {
  eel.openOverallDir()();
}

document.getElementById("Ebtn").addEventListener("click", toggleEbtn);
function toggleEbtn() {
  eel.openExcel()();
}

// toggleIbtn()
document.addEventListener("click", function (e) {
  if (e.target && e.target.parentNode.className == "idsbtn") {
    var id = e.target.parentNode.name;
    eel.openMangaFolder(id)();
  }
});

document.getElementsByClassName("trash")[0].addEventListener("click", toggleCbtn);
function toggleCbtn() {
  eel.ClnCovercache()();
  var ids = document.querySelectorAll(".idsbtn");
  Array.prototype.forEach.call(ids, function (id) {
    id.parentNode.removeChild(id);
  });
}

var repeat;
function moveLeft() {
  document.getElementsByClassName("overall-list")[1].scrollLeft -= 20;
}
function moveRight() {
  document.getElementsByClassName("overall-list")[1].scrollLeft += 20;
}

function clearmovelist() {
  clearInterval(repeater);
}

function addIdsLink(MangaCover, book) {
  var btn = document.createElement("button");
  var img = document.createElement("img");
  var div = document.createElement("div");

  // Add a button
  var olist = document.getElementsByClassName("overall-list")[1];
  olist.appendChild(btn);
  btn.setAttribute("class", "idsbtn");
  btn.setAttribute("name", book);

  // Add the img, span by selecting btn name
  var elementBtn = document.getElementsByName(book)[0];
  elementBtn.appendChild(img);
  elementBtn.appendChild(div);
  img.setAttribute("src", MangaCover + book + ".jpg");
  img.setAttribute("style", "width: inherit; height: inherit;");
  div.appendChild(document.createTextNode(book));
}
