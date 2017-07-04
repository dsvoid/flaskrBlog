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

function addTag(tag) {
	if(tag.value.indexOf(',') == 0) {
		tag.value = "";
	}
	if(tag.value.indexOf(',') != -1) {
		var tagValue = tag.value.replace(/,/g, "");

		var form = document.getElementById("edit-post");
		var tagView = document.getElementById("tags");
		var tagCount = form.getElementsByClassName("hidden-tag").length;

		var newTag = document.createElement("input");
		newTag.setAttribute("type", "hidden");
		newTag.setAttribute("class", "hidden-tag");
		newTag.setAttribute("name", "tag_" + tagCount);
		newTag.setAttribute("id", "tag_" + tagCount);
		newTag.setAttribute("value", tagValue);
		form.appendChild(newTag);

		var liTag = document.createElement("li");
		liTag.setAttribute("id", "tagView_" + tagCount);
		liTag.innerHTML = tagValue;
		tagView.appendChild(liTag);

		tag.value = "";
	}
}

