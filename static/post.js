function editBoxPopup() {

    //Init vars and show popup
    //Get the value field of input text to put it in popup text area

    var postContent;
    postContent = document.getElementById("post-content").innerHTML;
    document.getElementById("editBoxText").value = postContent;

    var popUp = $("#editBox");
    popUp.find(".editBoxOk,.editBoxCancel").unbind().click(function () {
        popUp.hide();
    });
    popUp.find(".editBoxOk").click(editYesFn);
    popUp.find(".editBoxCancel").click(noFn);
    popUp.show();
}

function deleteBoxPopup() {

    //Init vars and show popup

    var popUp = $("#deleteBox");
    popUp.find(".deleteBoxOk,.deleteBoxCancel").unbind().click(function () {
        popUp.hide();
    });
    popUp.find(".deleteBoxMsg").text("Are you sure you want to delete this post?");
    popUp.find(".deleteBoxOk").click(deleteYesFn);
    popUp.find(".deleteBoxCancel").click(noFn);
    popUp.show();
}

function editYesFn() {

    //Get the content of the text area and apply the changes to the post

    var newPost;
    newPost = document.getElementById("editBoxText").value;
    document.getElementById("post-content").innerHTML = newPost;
}

function deleteYesFn() {
    //Going back to Feed page
    window.location.replace("/feed");
}

function noFn() {
    //Nothing eh
}