function preview() {
	var output = markdown.toHTML(document.getElementById('text-input').value);
	document.getElementById("preview-text").innerHTML = output;
	document.getElementById("preview-title").innerHTML = document.getElementById('title-input').value;
	if(document.getElementById("preview-text").style.display == "none") {
		document.getElementById("preview-text").style.display = "block";
		document.getElementById("preview-title").style.display = "block";
		document.getElementById("edit-post").style.display = "none";
	} else {
		document.getElementById("preview-text").style.display = "none";
		document.getElementById("preview-title").style.display = "none";
		document.getElementById("edit-post").style.display = "block";
	}
}
