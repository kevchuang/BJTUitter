function editBoxPopup(postId) {

    //Init vars and show popup
    //Get the value field of input text to put it in popup text area

    var postContent;
    postContent = document.getElementById("post-content").innerHTML;
    document.getElementById("editBoxText").value = postContent;

    var popup = document.getElementById("editBox").innerHTML;
    document.getElementById("editBoxOk").addEventListener("click", hideBox);
    document.getElementById("editBoxOk").addEventListener("click", editYesFn(postId));
    document.getElementById("editBoxCancel").addEventListener("click", hideBox);
    document.getElementById("editBoxCancel").addEventListener("click", noFn);
    document.getElementById("editBox").style.display = "block";
}

function deleteBoxPopup() {

    //Init vars and show popup

    var popup = document.getElementById("deleteBox").innerHTML;
    document.getElementById("deleteBoxOk").addEventListener("click", hideBox);
    document.getElementById("deleteBoxOk").addEventListener("click", deleteYesFn);
    document.getElementById("deleteBoxCancel").addEventListener("click", hideBox);
    document.getElementById("deleteBoxCancel").addEventListener("click", noFn);
    document.getElementById("deleteBox").style.display = "block";
}

function hideBox() {
    document.getElementById("editBox").style.display = "none"
}


function editYesFn(postId) {

    //Get the content of the text area and apply the changes to the post

    var newPost;
    newPost = document.getElementById("editBoxText").value;
    document.getElementById("post-content").innerHTML = newPost;

    $.ajax({
        type: "POST",
        url: "TA ROUTE ICI VIVI",
        data: {
            "postid": postId,
            "value": newPost
        }
    }).done(function() {
        //Nothing to do
    });
}

function deleteYesFn() {
    //Going back to Feed page
    window.location.replace("/feed");
}

function noFn() {
    //Nothing eh
}