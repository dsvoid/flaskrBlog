var contents = document.getElementsByClassName("content");
console.log(contents[0]);
for(i = 0; i < contents.length; i++) {
	var element = contents[i];
	var post = element.parentNode;
	if (element.scrollHeight > element.clientHeight) {
		var keepReading = document.createElement("div");
		keepReading.setAttribute("class", "keep-reading");
		var link = post.getElementsByTagName("h1")[0].childNodes[0].getAttribute("href");
		keepReading.innerHTML = "<a href="+link+">Keep Reading</a>";
		var tags = post.getElementsByClassName("tags")[0];
		post.insertBefore(keepReading, tags);
	}
}
