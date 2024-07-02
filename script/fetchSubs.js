import subscribers from "../.git";

function fetchSubs() {
  var subsTag = document.getElementById("subs-list");
  subsTag.innerHTML = subscribers;

  console.log(subscribers);
}

fetchSubs();
