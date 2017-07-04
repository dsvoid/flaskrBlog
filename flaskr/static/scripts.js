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

		// create hidden input
		var newTag = document.createElement("input");
		newTag.setAttribute("type", "hidden");
		newTag.setAttribute("class", "hidden-tag");
		newTag.setAttribute("name", "tag_" + tagCount);
		newTag.setAttribute("id", "tag_" + tagCount);
		newTag.setAttribute("value", tagValue);
		form.appendChild(newTag);

		// create visible tag
		var liTag = document.createElement("li");
		liTag.setAttribute("id", "tagView_" + tagCount);
		liTag.setAttribute("class", "list-tag");
		liTag.innerHTML = tagValue + "<button type='button' class='delete-tag' onclick='deleteTag(this.parentNode)'>x</button>";
		tagView.appendChild(liTag);

		tag.value = "";
	}
}

function deleteTag(tag) {
	// remove tags
	var id = tag.id.split("_")[1];
	var inputTag = document.getElementById("tag_"+id);
	tag.parentNode.removeChild(tag);
	inputTag.parentNode.removeChild(inputTag);

	//recount tags
	var inputTags = document.getElementsByClassName("hidden-tag");
	var liTags = document.getElementsByClassName("list-tag");
	for(i = 0; i < liTags.length; i++) {
		inputTags[i].setAttribute("name", "tag_" + i);
		liTags[i].setAttribute("name", "tagView_" + i);
		inputTags[i].setAttribute("id", "tag_" + i);
		liTags[i].setAttribute("id", "tagView_" + i);
	}
}
